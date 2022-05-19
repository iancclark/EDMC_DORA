import logging
import os
import semantic_version
from typing import Optional, Dict, Any
import json

import tkinter as tk
from tkinter import ttk
import myNotebook as nb
from theme import theme

from config import appname, appversion
import timeout_session

plugin_name=os.path.basename(os.path.dirname(__file__))
logger=logging.getLogger(f'{appname}.{plugin_name}')

SCAN_STAR_TO_EDSMBODY={
        "BodyName":"name",
        "BodyID":"bodyID",
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
        "BodyID":"bodyID",
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

this = This()

def plugin_start3(plugin_dir: str) -> str:
    return plugin_name

def plugin_app(parent: tk.Frame) -> tk.Frame:
    this.frame = tk.Frame(parent)
    draw_UI()
    return this.frame

def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str,Any], state: Dict[str, Any]) -> None:
    # Think about using match
    if entry['event'] in ('FSDJump','CarrierJump','Location'):
        # We have loaded/died/arrived somewhere

        # Get cached data, fallback to EDSM
        get_bodies(event['SystemAddress'])

        # clear tree 
        for item in this.tree.get_children():
            this.tree.delete(item)
        if not this.systeminfo['bodyCount']:
            this.header.config(text='Honk required')
        else:
            this.header.config(text=f'Astro: {this.systeminfo["bodies"].len()}/{systeminfo["bodyCount"]}')
        # fill tree
        fill_Tree()
        return None

    if entry['event'] == 'FSSDiscoveryScan':
        # honk!
        this.header.config(text=f'0/{event["BodyCount"]}')
        this.systeminfo["bodyCount"]=event["BodyCount"]
        return None
    # more detailed scan, 
    if entry['event'] == 'Scan':
        # Useful info:
        #   BodyName, BodyID, Parents, SystemAddress, PlanetClass, Atmosphere,
        #   Volcanism, MassEM, Radius, Landable, WasDiscovered, WasMapped
        #   ScanType (Basic, Detailed, NavBeacon, NavBeaconDetail, AutoScan)
        body={}
        if "PlanetClass" in entry.keys():
            for scankey,edsmkey in SCAN_PLANET_TO_EDSMBODY:
                body[edsmkey]=entry[scankey]
        elif "StarType" in entry.keys():
            for scankey,edsmkey in SCAN_STAR_TO_EDSMBODY:
                body[edsmkey]=entry[scankey]
        this.systeminfo['bodies'].push(body)
        fill_Tree()
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
        # Find the bodyid, set "dssScanned: true"
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
        r=session.get(f'https://www.edsm.net/api-system-v1/bodies?systemId64={systemid}')
        r.raise_for_status()
        this.system=r.json()
        for body in this.system['bodies']:
            body['scanType']="EDSM"
    except Exception as e:
        logger.warning('Problem when getting system info from EDSM')

def get_cached_bodies(systemid: int) -> bool:
    # open a file lol.
    file=f'{systemid:016x}.json'
    subdir=file[0,1]
    if os.path.exists(f'data/{subdir}/{file}'):
        with open(f'data/{subdir}/{file}', r) as f:
            this.systeminfo=json.load(f)
            return True
    return False

def get_bodies(systemid: int) -> None:
    if not get_cached_bodies(systemid):
        get_edsm_bodies(systemid)

def draw_UI()->None:
    this.frame.rowconfigure(1,weight=1)
    this.frame.rowconfigure(0,weight=1)
    this.frame.columnconfigure(0,weight=1)
    this.header = ttk.Label(this.frame,wraplength=200,justify="left",text="D O R A - Awaiting initialisation")
    this.header.grid(row=0,sticky=tk.EW)
    this.tree = ttk.Treeview(this.frame,columns=('Class'))
    this.tree.column("#0",width=100,minwidth=50,stretch="yes");
    this.tree.column("Class",width=100,minwidth=50,stretch="yes");
    this.tree.heading('#0',text="Body Name")
    this.tree.heading('Class',text="Class")
    this.tree.grid(row=1,sticky=tk.EW)
    theme.update(this.frame)

def fill_Tree()->None:
    # fill the tree from this.systeminfo.
    return None
