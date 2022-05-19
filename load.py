import logging
import os
import semantic_version
from typing import Optional, Dict, Any

import tkinter as tk
from tkinter import ttk
import myNotebook as nb
from theme import theme

from config import appname, appversion

plugin_name=os.path.basename(os.path.dirname(__file__))
logger=logging.getLogger(f'{appname}.{plugin_name}')

head: Optional[ttk.Label] = None
tree: Optional[ttk.Treeview] = None

if not logger.hasHandlers():
    level = logging.INFO
    logger.setLevel(level)
    logger_channel=logging.StreamHandler()
    logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)

def plugin_start3(plugin_dir: str) -> str:
    return plugin_name

def plugin_app(parent: tk.Frame) -> tk.Frame:
    global tree
    frame = tk.Frame(parent)
    frame.rowconfigure(1,weight=1)
    frame.rowconfigure(0,weight=1)
    frame.columnconfigure(0,weight=1)
    head = ttk.Label(frame,wraplength=200,justify="left",text="")
    head.grid(row=0,sticky=tk.EW)
    tree = ttk.Treeview(frame,columns=('Class'))
    tree.column("#0",width=100,minwidth=50,stretch="yes");
    tree.column("Class",width=100,minwidth=50,stretch="yes");
    tree.heading('#0',text="Body Name")
    tree.heading('Class',text="Class")
    tree.grid(row=1,sticky=tk.EW)
    theme.update(frame)
    return frame

def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str,Any], state: Dict[str, Any]) -> None:
    global tree

    # Think about using match
    if entry['event'] in ('FSDJump','CarrierJump'):
        # We have arrived somewhere
        # clear body list. 
        # Maybe get data from edsm, eddiscovery seems to do this. 
        #   https://www.edsm.net/api-system-v1/bodies?systemName={name}
        #   https://www.edsm.net/api-system-v1/bodies?systemId64={id}
        # Maybe a sqlite cache? Or just json on disk?
        # Useful info:
        #   StarSystem, SystemAddress
        for item in tree.get_children():
            tree.delete(item)
        return None
    if entry['event'] == 'FSSDiscoveryScan':
        # honk!
        # Useful info:
        #   Bodycount, SystemName, SystemAddress, Progress
        head.config(text=f'{event["progress"]*event["bodycount"]}/{event["Bodycount"]}')
        return None
    # more detailed scan, Basic, Detailed, NavBeacon, NavBeaconDetail, AutoScan
    if entry['event'] == 'Scan':
        # Useful info:
        #   BodyName, BodyID, Parents[0], SystemAddress, PlanetClass, Atmosphere,
        #   Volcanism, MassEM, Radius, Landable, WasDiscovered, WasMapped

        if "PlanetClass" in entry.keys():
            if tree.exists(entry['BodyID']):
                # update
                tree.item(entry['BodyID'],text=entry['BodyName'],values=(entry['PlanetClass'],entry['DistanceFromArrivalLS']))
            else:
                parentid=parental_placeholders(entry['Parents'])
                tree.insert(parentid,0,iid=entry['BodyID'],open=True,text=entry['BodyName'],values=(entry['PlanetClass'],entry['DistanceFromArrivalLS']))
        elif "StarType" in entry.keys():
            if tree.exists(entry['BodyID']):
                # update
                tree.item(entry['BodyID'],text=entry['BodyName'],values=(entry['StarType'],entry['DistanceFromArrivalLS']))
            else:
                parentid=parental_placeholders(entry['Parents'])
                tree.insert(parentid,0,iid=entry['BodyID'],open=True,text=entry['BodyName'],values=(entry['StarType'],entry['DistanceFromArrivalLS']))

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
    global tree
    parentiid=0
    # Find out if parent exists. If not, create
    for p in reversed(parents):
        for obj,iid in p.items():
            if not tree.exists(iid):
                if parentiid == iid:
                    tree.insert('',0,iid=iid,open=True,text="?",values=(f'{obj}'))
                else:
                    tree.insert(parentiid,0,iid=iid,open=True,text="?",values=(f'{obj}'))
            parentiid=iid
    return parentiid

