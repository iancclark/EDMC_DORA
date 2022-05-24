import logging
import os
import semantic_version
from typing import Optional, Dict, Any
import json
from threading import Timer
from time import sleep

import tkinter as tk
from tkinter import ttk
import myNotebook as nb
from theme import theme

from config import appname, appversion, config
import timeout_session

plugin_name=os.path.basename(os.path.dirname(__file__))
logger=logging.getLogger(f'{appname}.{plugin_name}')

SCAN_STAR_TO_EDSMBODY={
        "BodyName":"name",
        "BodyID":"bodyId",
        "Parents":"parents",
        "DistanceFromArrivalLS":"distanceToArrival", 
        "StarType":"subType", # rough match
        "Subclass":"spectralClass", # very rough match
        "StellarMass":"solarMasses",
        "Radius":"solarRadius", # units wrong
        "AbsoluteMagnitude":"absoluteMagnitude",
        "Age_MY":"age",
        "SurfaceTemperature":"surfaceTemperature",
        "Luminosity":"luminosity",
        "SemiMajorAxis":"semiMajorAxis",
        "Eccentricity":"orbitalEccentricity",
        "OrbitalInclination":"orbitalInclination",
        "Periapsis":"argOfPeriapsis",
        "OrbitalPeriod":"orbitalPeriod",
        "RotationalPeriod":"rotationalPeriod", # units wrong
        "AxialTilt":"axialTilt"
        }
SCAN_PLANET_TO_EDSMBODY={
        "BodyName":"name",
        "BodyID":"bodyId",
        "Parents":"parents",
        "DistanceFromArrivalLS":"distanceToArrival",
        "TidalLock":"rotationalPeriodTidallyLocked",
        "TerraformState":"terraformingState",
        "PlanetClass":"subType", # rough match
        "AtmosphereType":"atmosphereType", # rough match
        "AtmosphereComposition":"atmosphereComposition", # rough match
        "Volcanism":"volcanismType",
        "MassEM":"earthMasses",
        "Radius":"radius", # units wrong
        "SurfaceGravity":"gravity",
        "SurfaceTemperature":"surfaceTemperature",
        "SurfacePressure":"surfacePressure",
        "Landable":"isLandable",
        "Composition":"solidComposition",
        "SemiMajorAxis":"semiMajorAxis",
        "Eccentricity":"orbitalEccentricity",
        "OrbitalInclination":"orbitalInclination",
        "OrbitalPeriod":"orbitalPeriod",
        "RotationalPeriod":"rotationalPeriod", # units wrong
        "AxialTilt":"axialTilt"
        }
TREE_COLUMNS=[
        {"name":"class","header":"Class","field":"subType","show":True,"width":20},
        {"name":"dist","header":"Arr.Dist","field":"distanceToArrival","show":True,"width":20},
        {"name":"grav","header":"Gravity","field":"gravity","show":True,"width":20},
        {"name":"temp","header":"Temp","field":"surfaceTemperature","show":True,"width":20},
        {"name":"atmo","header":"Atm","field":"atmosphereType","show":True,"width":20},
        {"name":"land","header":"Land","field":"isLandable","show":True,"width":5}]

if not logger.hasHandlers():
    level = logging.INFO
    logger.setLevel(level)
    logger_channel=logging.StreamHandler()
    logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)

class This:
    def __init__(self):
        self.frame: tk.Frame = None
        self.header: ttk.Label = None
        self.tree: ttk.Treeview = None
        self.session = timeout_session.new_session()
        self.systeminfo: Dict = {}
        self.systemid: Int = None
        self.datadir=f'{os.path.dirname(__file__)}/data'
        self.timer: Timer = None

this = This()

def plugin_start3(plugin_dir: str) -> str:
    this.timer=Timer(30,timedsave)
    return plugin_name

def plugin_app(parent: tk.Frame) -> tk.Frame:
    this.frame = tk.Frame(parent)
    draw_UI()
    #get_bodies(0x0000149c280025a9)
    #fill_Tree()
    return this.frame

def cmdr_data(data:Dict[str,Any], is_beta: bool)->None:
    logger.info("Cmdr data")
    if this.systemid == None and data.get("starsystem") and data.get("systemaddress"):
        this.systemid=data.get("starsystem").get("systemaddress")
        get_bodies(this.systemid)
    return None

def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str,Any], state: Dict[str, Any]) -> None:
    # Think about using match
    if entry['event'] in ('FSDJump','CarrierJump','Location'):
        # We have loaded/died/arrived somewhere
        
        # Save any existing data
        if "bodyDict" in this.systeminfo and this.systemid==this.systeminfo.id64:
            save_bodies(this.systemid)
        this.systemid=entry['SystemAddress']

        # Get cached data, fallback to EDSM
        get_bodies(entry['SystemAddress'])

        # clear tree 
        for item in this.tree.get_children():
            this.tree.delete(item)
        if not this.systeminfo['bodyCount']:
            this.header.config(text='Honk required')
        else:
            header_text()
        # fill tree
        fill_Tree()
        return None

    if entry['event'] == 'FSSDiscoveryScan':
        # honk!
        this.systeminfo["bodyCount"]=entry["BodyCount"]
        # What to do if no bodydict...
        # TODO check body systemaddress against current systemaddress
        get_bodies(entry['SystemAddress'])
        header_text()
        fill_Tree()
        return None
    # more detailed scan, 
    if entry['event'] == 'Scan':
        # Useful info:
        #   BodyName, BodyID, Parents, SystemAddress, PlanetClass, Atmosphere,
        #   Volcanism, MassEM, Radius, Landable, WasDiscovered, WasMapped
        #   ScanType (Basic, Detailed, NavBeacon, NavBeaconDetail, AutoScan)
        # TODO check body systemaddress against current systemaddress
        body={"scanType":entry["ScanType"]}
        if "PlanetClass" in entry.keys():
            body["type"]="Planet"
            for scankey,edsmkey in SCAN_PLANET_TO_EDSMBODY.items():
                if scankey in entry.keys():
                    body[edsmkey]=entry[scankey]
        elif "StarType" in entry.keys():
            for scankey,edsmkey in SCAN_STAR_TO_EDSMBODY.items():
                if scankey in entry.keys():
                    body[edsmkey]=entry[scankey]
        # find item in list
        if not 'bodyDict' in this.systeminfo:
            this.systeminfo['bodyDict']={}
        this.systeminfo['bodyDict'][entry['BodyID']]=body
        fill_Tree()
        if this.timer.is_alive():
            this.timer.cancel()
        this.timer=Timer(30,timedsave)
        this.timer.start()
        header_text()
        return None
    if entry['event'] == "FSSBodySignals":
        # Surface stuff, e.g. bio/vulc.
        # Useful info:
        # [ "Type":"$SAA_SignalType_{x}", "Count":{y} ]
        # Biological, Geological
        return None
    # DSS done
    if entry['event'] == 'SAAScanComplete': 
        # Useful info:
        #  BodyID
        # Find the bodyid, set "mapped: true"
        this.systeminfo["bodyDict"][entry["bodyId"]]["mapped"]=True
        if this.timer.is_alive():
            this.timer.cancel()
        this.timer=Timer(30,timedsave)
        this.timer.start()
        header_text()
        fill_Tree()
        return None
    # centre of gravity of pair
    if entry['event']=='ScanBaryCentre': 
        return None
    return None

def parental_placeholders(parents: list) -> int:
    """
    Parent info from a scan is a list of ordered dictionaries, starting with
    the direct parent, then parent's parent etc. Annoyingly, each parent is in
    a dict, with type of parent as the key and the bodyid as the value.

    If we don't already have the parent(s) in the tree we'll add placeholders
    """
    parentiid=0
    if parents is None:
        return ''
    # Find out if parent exists. If not, create
    for p in reversed(parents):
        for obj,iid in p.items():
            if not this.tree.exists(iid):
                if parentiid == iid:
                    this.tree.insert('',0,iid=iid,open=True,text="?",values=(f'{obj}'))
                else:
                    this.tree.insert(parentiid,0,iid=iid,open=True,text="?",values=(f'{obj}'))
            parentiid=iid
    return parentiid

def get_edsm_bodies(systemid: int) -> None:
    try:
        r=this.session.get(f'https://www.edsm.net/api-system-v1/bodies?systemId64={systemid}')
        r.raise_for_status()
        this.systeminfo=r.json()
        # I don't like the way EDSM saves bodies. There. I've said it.
        this.systeminfo['bodyDict']={}
        for body in this.systeminfo['bodies']:
            body['scanType']="EDSM"
            this.systeminfo['bodyDict'][body['bodyId']]=body;
    except Exception as e:
        logger.warning('Problem when getting system info from EDSM: {0}'.format(e))
    save_bodies(systemid)

def get_cached_bodies(path) -> bool:
    if os.path.exists(path):
        with open(path, 'r') as f:
            this.systeminfo=json.load(f)
            return True
    return False

def save_bodies(systemid: int) -> None:
    try:
        with open(systemid_path(systemid),'w') as f:
            json.dump(this.systeminfo,f)
    except Exception as e:
        logger.warning('Problem saving scan data to file: {0}'.format(e))


def systemid_path(systemid: int) -> str:
    file=f'{systemid:016x}.json'
    subdir=file[0:2]
    os.makedirs(f'{this.datadir}/{subdir}',exist_ok=True)
    return f'{this.datadir}/{subdir}/{file}'

def get_bodies(systemid: int) -> None:
    if not get_cached_bodies(systemid_path(systemid)):
        get_edsm_bodies(systemid)

def draw_UI()->None:
    this.frame.rowconfigure(1,weight=1)
    this.frame.rowconfigure(0,weight=1)
    this.frame.columnconfigure(0,weight=1)
    this.header = ttk.Label(this.frame,wraplength=200,justify="left",text="D O R A - Awaiting initialisation")
    this.header.grid(row=0,columnspan=2,sticky=tk.EW)
    # #0 is a special case :|
    this.tree = ttk.Treeview(this.frame,
            columns=[colinfo["name"] for colinfo in TREE_COLUMNS],
            displaycolumns=[colinfo["name"] for colinfo in TREE_COLUMNS if colinfo["show"]],
            style="dora.Treeview")
    this.tree.column("#0",minwidth=50,width=50,stretch="yes")
    this.tree.heading("#0",text="Body name")

    style=ttk.Style()
    # Win32 theme doesn't let us change the appearance much. Some tricks here perhaps:
    #  https://stackoverflow.com/questions/42708050/tkinter-treeview-heading-styling/42738716#42738716
    style.theme_use("default")
    style.map("dora.Treeview.Heading",
            background=[('active','#ff8800'),('pressed','!focus','#303030')],
            foreground=[('active','black'),('pressed','!focus','#ff8800')]
        )
    style.configure('dora.Treeview',font=(None,8),foreground='#ff8800',background='#181818',fieldbackground='#181818',)
    style.configure('dora.Treeview.Heading',foreground='#ff8800',background='#303030')
    style.configure('Vertical.Scrollbar',arrowcolor='#ff8800',background='#303030',troughcolor='black')
    style.configure('TSizegrip',background='black',foreground='#ff8800')
    this.tree.tag_configure('scanned',font=(None,8,"bold"))
    this.tree.tag_configure('known',font=(None,8,"italic"))
    this.tree.tag_configure('mapped',foreground='blue')

    for colinfo in TREE_COLUMNS:
        this.tree.column(colinfo["name"],width=20,minwidth=colinfo["width"],stretch="yes")
        this.tree.heading(colinfo["name"],text=colinfo["header"])

    scrollbar=ttk.Scrollbar(this.frame,orient=tk.VERTICAL, command=this.tree.yview)
    this.tree.configure(yscroll=scrollbar.set)
    this.tree.grid(row=1,column=0,sticky=tk.EW)
    scrollbar.grid(row=1,column=1,sticky=tk.NS)
    grabber=ttk.Sizegrip(this.frame)
    grabber.grid(row=2,column=1,sticky=tk.SE)
    theme.update(this.frame)

def fill_Tree()->None:
    # fill the tree from this.systeminfo.
    if "bodyDict" not in this.systeminfo:
        logger.info("No body info to use yet")
        return
    for bodyId,body in this.systeminfo['bodyDict'].items():
        if "name" not in body:
            continue
        data: list[str]=[] 
        tags: list[str]=[]
        for field in [colinfo['field'] for colinfo in TREE_COLUMNS]:
            if field in body:
                data.append(body[field])
            else:
                data.append("")
        parent=parental_placeholders(body['parents'])
        if body.get("mapped"):
            tags.append("mapped")
        else:
            tags.append("unmapped")
        if body.get("scanType") == "EDSM":
            tags.append("known")
        else:
            tags.append("scanned")
        if this.tree.exists(bodyId):
            this.tree.item(bodyId,values=data,open=True,tags=tags)
        else:
            this.tree.insert(parent,tk.END,iid=bodyId,text=body["name"],values=data,open=True,tags=tags)

    return None

def timedsave()->None:
    while not config.shutting_down:
        if this.systemid is not None:
            save_bodies(this.systemid)

def header_text()->None:
    # check the fields we want to use exist :(
    total_bodies=this.systeminfo.get("bodyCount")
    total_planets=len([k for k,v in this.systeminfo["bodyDict"].items() if v.get("type")=="Planet"])
    self_scanned=len([k for k,v in this.systeminfo["bodyDict"].items() if v.get("scanType") != "EDSM"])
    self_mapped=len([k for k,v in this.systeminfo["bodyDict"].items() if "mapped" in v.keys()])
    this.header.config(text=f'Astro: {self_scanned}/{total_bodies} Surface: {self_mapped}/{total_planets}')
