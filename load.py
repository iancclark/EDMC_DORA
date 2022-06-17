import logging
import os
import semantic_version
from typing import Optional, Dict, Any
import json
from threading import Timer

import tkinter as tk
from tkinter import ttk
import myNotebook as nb
from theme import theme

from config import appname, appversion, config
import timeout_session

import system

plugin_name=os.path.basename(os.path.dirname(__file__))
logger=logging.getLogger(f'{appname}.{plugin_name}')

TREE_COLUMNS=[
        {"name":"class","header":"Class","field":"subType","show":True,"width":20, "anchor":tk.W,"format":"{}"},
        {"name":"dist","header":"Arr.Dist","field":"distanceToArrival","show":True,"width":20,"anchor":tk.E,"format":"{:.0f}LS"},
        {"name":"grav","header":"Gravity","field":"gravity","show":True,"width":20,"anchor":tk.E,"format":"{:.2f}g"},
        {"name":"temp","header":"Temp","field":"surfaceTemperature","show":True,"width":20,"anchor":tk.E,"format":"{:.0f}K"},
        {"name":"atmo","header":"Atm","field":"atmosphereType","show":True,"width":20,"anchor":tk.W,"format":"{}"},
        {"name":"land","header":"Actions","field":"actions","show":True,"width":5,"anchor":tk.W,"format":"{}"},
        {"name":"geoSignals","header":"Geo","field":"geoSignals","show":True,"width":5,"anchor":tk.W,"format":"{}"},
        {"name":"bioSignals","header":"Bio","field":"bioSignals","show":True,"width":5,"anchor":tk.W,"format":"{}"},
        ]

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
        self.status: ttk.Label = None
        self.tree: ttk.Treeview = None
        self.system: system = None
        self.timer=None

this = This()

def plugin_start3(plugin_dir: str) -> str:
    return plugin_name

def plugin_app(parent: tk.Frame) -> tk.Frame:
    this.frame = tk.Frame(parent)
    this.system = system.System()
    draw_UI()
    this.tree.bind_all('<<DORARefresh>>', refresh)
    #fill_Tree()
    #dora_status()
    delayed_update()
    return this.frame

def cmdr_data(data:Dict[str,Any], is_beta: bool)->None:
    logger.info("Cmdr data")
    #if this.systemid == None and data.get("starsystem") and data.get("systemaddress"):
        # might be nice to get saved data?
    #    return None
    return None

def plugin_stop()->None:
    # perhaps save?
    this.system.shut()
    return

def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str,Any], state: Dict[str, Any]) -> None:
    # Think about using match
    if entry['event'] in ('FSDJump','CarrierJump','Location'):
        logger.info(f'FSDJump or similar: {entry["SystemAddress"]}')
        this.system.fsdjump(entry)
        # fill tree
        #dora_status()
        #fill_Tree()
        delayed_update()
        return None

    if entry['event'] == 'FSSDiscoveryScan':
        # honk!
        this.system.fsshonk(entry)
        #dora_status()
        #fill_Tree()
        delayed_update()
        return None

    # more detailed scan, 
    if entry['event'] == 'Scan':
        logger.info(f'Scan({entry["ScanType"]}) : {entry["SystemAddress"]}')
        this.system.scan(entry)
        #dora_status()
        #fill_Tree()
        delayed_update()
        return None
    if entry['event'] == "FSSBodySignals":
        logger.info(f'BodySignals: {entry["SystemAddress"]}')
        this.system.fsssignals(entry)
        dora_status()
        return None
    # DSS done
    if entry['event'] == 'SAAScanComplete': 
        logger.info(f'SurfaceScanComplete: {entry["SystemAddress"]}')
        this.system.dssscan(entry)
        #dora_status()
        #fill_Tree()
        delayed_update()
        this.tree.see(entry['BodyID'])
        return None
    return None

def draw_UI()->None:
    this.frame.rowconfigure(1,weight=1)
    this.frame.rowconfigure(0,weight=1)
    this.frame.columnconfigure(0,weight=1)
    this.status = ttk.Label(this.frame,wraplength=200,justify="left",text="D O R A - Awaiting initialisation")
    this.status.grid(row=0,columnspan=2,sticky=tk.EW)
    this.displaymode=tk.Button(this.frame,text="Collapse mapped",command=displayMode)
    this.displaymode.grid(row=0,sticky=tk.E)
    # #0 is a special case :|
    this.tree = ttk.Treeview(this.frame,
            columns=[colinfo["name"] for colinfo in TREE_COLUMNS],
            displaycolumns=[colinfo["name"] for colinfo in TREE_COLUMNS if colinfo["show"]],
            style="dora.Treeview")
    this.tree.column("#0",minwidth=50,width=50,stretch="yes")
    this.tree.heading("#0",text="Body name")

    this.tree.bind("<Double-1>", treeDblClick)

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
    this.tree.tag_configure('mapped',foreground='cyan')
    this.tree.tag_configure('selfmapped',foreground='blue')

    for colinfo in TREE_COLUMNS:
        this.tree.column(colinfo["name"],width=20,minwidth=colinfo["width"],stretch="yes",anchor=colinfo["anchor"])
        this.tree.heading(colinfo["name"],text=colinfo["header"])

    scrollbar=ttk.Scrollbar(this.frame,orient=tk.VERTICAL, command=this.tree.yview)
    this.tree.configure(yscroll=scrollbar.set)
    this.tree.grid(row=1,column=0,sticky=tk.EW)
    scrollbar.grid(row=1,column=1,sticky=tk.NS)
    # This grabber allows resizing with themed EDMC window
    grabber=ttk.Sizegrip(this.frame)
    grabber.grid(row=2,column=1,sticky=tk.SE)
    theme.update(this.frame)

def fill_Tree()->None:
    # clear tree 
    for item in this.tree.get_children():
        this.tree.delete(item)
    for body in this.system.knownbodies():
        if this.displaymode['text'].startswith("Collapse"):
            openitem=False
        else:
            openitem=True
        if body['type']=="Planet":
            shortname=body["name"].replace(this.system.systemname()+" ","")
        elif body.get("type") == "Null":
            if body.get("name"):
                shortname=body['name'].replace(this.system.systemname()+" ","")
            else:
                # probably a barycentre, maybe a nice improvement would be to put short names of bodies here, comma separated?
                shortname=f"\u047a"
        elif body.get("type")=="Ring":
            shortname="\u25cc"
        elif body.get("name"):
            shortname=body["name"]
        else:
            logger.warn(f"Missing name for {body}")
        data: list[str]=[] 
        tags: list[str]=[]
        for field,fmt in [(colinfo['field'],colinfo['format']) for colinfo in TREE_COLUMNS]:
            if field in body:
                data.append(fmt.format(body[field]))
            else:
                data.append("")

        if body.get("type")=="Planet":
            if body.get("mapped")=="self":
                tags.append("selfmapped")
            elif body.get("mapped")=="other":
                tags.append("mapped")
                # expand parent
                tree_expand(body.get('parentId'))
            else:
                # expand parent
                tree_expand(body.get('parentId'))

        if body.get("scanType") == "EDSM":
            tags.append("known")
        else:
            tags.append("scanned")
        if this.tree.exists(body['bodyId']):
            this.tree.item(body['bodyId'],values=data,open=openitem,tags=tags)
        else:
            if this.tree.exists(body['parentId']):
                this.tree.insert(body["parentId"],tk.END,iid=body["bodyId"],text=shortname,values=data,open=openitem,tags=tags)
            else:
                this.tree.insert('',tk.END,iid=body["bodyId"],text=shortname,values=data,open=True,tags=tags)

    return None

def tree_expand(bodyId:int):
    if bodyId != None and this.tree.exists(bodyId) and this.displaymode['text']=="Collapse mapped":
        this.tree.item(bodyId,open=True)


def dora_status()->None:
    # check the fields we want to use exist :(
    # bodies, planets, scanned, mapped

    bodies=this.system.getBodyCount()
    kb=this.system.knownbodies() 
    scanned=len([x for x in kb if x['type'] in ('Planet','Star') and x['scanType']!="EDSM"])
    mapped=len([x for x in kb if x['type'] == 'Planet' and x.get('mapped')=='self'])
    planets=len([x for x in kb if x['type']=="Planet"])
    this.status.config(text=f'DORA: Scanned: {scanned}/{bodies} Mapped: {mapped}/{planets}')
    return

def treeDblClick(event):
    item=this.tree.identify('item',event.x,event.y)
    if item!='':
        logger.info(f"DoubleClicked bodyId {item}")
        idx=int(item)
        widget=this.tree.item(idx,"tags")
        logger.info(f"Tags: {widget}")
        logger.info(f"Details: {this.system.bodies[idx]}")

def tick():
    # trigger save
    # trigger UI redraw
    this.tree.event_generate('<<DORARefresh>>')
    this.system.to_file()
    logger.info("Ticked")

def delayed_update():
    if this.timer!=None and this.timer.is_alive():
        this.timer.cancel()
    this.timer=Timer(5,tick)
    this.timer.start()

def refresh(event):
    fill_Tree()
    dora_status()
    this.timer=None

def displayMode():
    if this.displaymode['text']=="Collapse mapped":
        this.displaymode['text']="Collapse all"
    elif this.displaymode['text']=="Collapse all":
        this.displaymode['text']="Expand all"
    else:
        this.displaymode['text']="Collapse mapped"
    fill_Tree()

    return
