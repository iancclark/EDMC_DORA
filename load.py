"""
Notes:
    https://hosting.zaonce.net/community/journal/v33/Journal_Manual_v33.pdf
    https://github.com/Marginal/HabZone/blob/master/load.py
    https://github.com/EDCD/EDMarketConnector/blob/main/PLUGINS.md
    https://github.com/EDDiscovery/EDDiscovery
"""

import logging
import os
import semantic_version
from typing import Optional, Dict, Any

import tkinter as tk
from tkinter import ttk

import myNotebook as nb
from theme import theme

from config import appname, appversion
from EDMCLogging import get_main_logger

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
    logger.info("Started")
    return plugin_name

def plugin_app(parent: tk.Frame) -> tk.Frame:
    global tree
    frame = tk.Frame(parent)
    head = ttk.Label(frame,wraplength=200,justify="left",text="")
    head.pack(side="top")
    tree = ttk.Treeview(frame,columns=('BodyName','Class'))
    tree.column(0,width=100);
    tree.column(1,width=100);
    tree.heading('BodyName',text="Body Name")
    tree.heading('Class',text="Class")
    tree.pack(side="left")
    #theme.update(this.frame)
    return frame

def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str,Any], state: Dict[str, Any]) -> None:
    global tree

    # Think about using match
    if entry['event'] not in ("FSDJump", "FSSDiscoveryScan","Scan","FSSBodySignals","SAAScanComplete","ScanBaryCentre"):
        return None
    if entry['event'] == 'FSDJump':
        # We have arrived somewhere
        # clear body list. 
        # Maybe get data from edsm, eddiscovery seems to do this. 
        #   https://www.edsm.net/api-system-v1/bodies?systemName={name}
        #   https://www.edsm.net/api-system-v1/bodies?systemId64={id}
        # Maybe a sqlite cache?
        # Useful info:
        #   StarSystem, SystemAddress
        return None
    if entry['event'] == 'FSSDiscoveryScan':
        # honk!
        # Useful info:
        #   Bodycount, SystemName, SystemAddress, Progress
        head['text']=f'{event["progress"]*event["bodycount"]}/{event["Bodycount"]}'
        return None
    # more detailed scan, Basic, Detailed, NavBeacon, NavBeaconDetail, AutoScan
    if entry['event'] == 'Scan':
        # Useful info:
        #   BodyName, BodyID, Parents[0], SystemAddress, PlanetClass, Atmosphere,
        #   Volcanism, MassEM, Radius, Landable, WasDiscovered, WasMapped

        ## TODO break out into a separate func
        # Find out if parent exists. If not, create
        heir=[ list(parent.values)[0] for parent in entry["parents"] ]
        for c,iid in enumerate(reversed(heir)):
            if not tree.item(iid):
               if c == 0:
                   tree.insert(0,iid=iid,values=("Unknown body","Unknown class"))
               else:
                   tree.insert(heir[c-1],iid=iid,values=("Unknown body","Unknown class"))
        tree.insert(heir[0],iid=event['BodyID'],values=(event['BodyName'],event['PlanetClass']))
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

