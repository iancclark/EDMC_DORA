import json
import logging
import os
from typing import Optional, Dict, Any
from SparseList import SparseList
import edsm
import journalscan
from config import appname,appversion,config

plugin_name=os.path.basename(os.path.dirname(__file__))
logger=logging.getLogger(f'{appname}.{plugin_name}')

if not logger.hasHandlers():
    level = logging.INFO
    logger.setLevel(level)
    logger.channel=logging.StreamHandler()
    logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)
    
class System:
    def __init__(self):
        self.systemAddress: int = 0
        self.systemName: str = ""
        self.bodyCount: int = 0
        self.bodies: SparseList = []
        self.datadir=f'{os.path.dirname(__file__)}/data'
        return None

    def from_edsm(self,systemAddress:int):
        if self.systemAddress !=0 and self.systemAddress != systemAddress:
            raise Exception("Asked to load data from EDSM when I have some data")
        # should already know systemname/address
        (self.bodies,self.bodyCount)=edsm.getsystem(systemAddress)
        # make the tree
        for body in self.bodies:
            if body != None:
                self._child_to_parents(body)
        return

    def from_file(self,systemAddress:int):
        if self.systemAddress !=0 and self.systemAddress != systemAddress:
            raise Exception("Asked to load data from file when I have some data")
        with open(self._filepath(systemAddress),'r') as f:
            self.__dict__=json.load(f)
        return

    def to_file(self,systemAddress:int):
        if self.systemAddress != systemAddress:
            raise Exception(f'Asked to save {systemAddress}, think we know about {self.systemAddress}')
        # make the dir
        savefile=self._filepath(systemAddress)

        os.makedirs(os.path.dirname(savefile),exist_ok=True)
        with open(savefile,'w') as f:
            json.dump(self.__dict__,f)

    def body_from_scan(self,data):
        if(data.get("systemAddress") != self.systemAddress):
            raise Exception(f'Received a scan for a different system')
        # create body by bodyid if necessary
        if self.bodies.get('BodyID'):
            body=self.bodies.get('BodyID')
        else:
            body={"bodyId":data['BodyID']}
        # call scan_to_body from journalscan.py
        body=journalscan.scan_to_body(data,body)
        self.bodies[data['BodyID']]=body
        self._child_to_parents(body)
        return

    def body_from_fsssignals(self,data):
        # find the appropriate body, pass onto journalscan.py bodysignals
        if self.bodies.get('BodyID'):
            body=self.bodies.get('BodyID')
        else:
            body={"bodyId":data['BodyID']}
        body=journalscan.bodysignals(data,body)
        self.bodies[data['BodyID']]=body
        return

    def fsdjump(self,data):
        # or carrierjump or location 
        # If we have data, and systemAddress different, rotate.
        if self.systemAddress != data['SystemAddress']:
            self.rotate()
            self.systemAddress=data['SystemAddress']
            self.systemName=data['StarSystem']

        # Try to restore from a save file
        try:
            self.from_file(data['SystemAddress'])
        except FileNotFoundError:
            # presumably the file is missing, try EDSM
            self.from_edsm(data['SystemAddress'])
        # Otherwise just the bare minimum, need a honk for more
        return

    def fsshonk(self,data):
        if(data.get("systemAddress") != self.systemAddress):
            raise Exception(f'Received a scan for a different system')
        # As above, fill in bodyCount
        self.bodyCount=data['BodyCount']
        return

    def body_from_dssscan(self,data):
        # get body id, set to mapped
        self.bodies[data['BodyID']]["mapped"]=True
        return

    def knownbodies(self)->list:
        return [body for body in self.bodies if body != None ]

    def rotate(self)->None:
        # save data
        if self.systemAddress != 0:
            self.to_file(self.systemAddress)
        # clear data
        self.systemAddress: int = 0
        self.systemName: str = ""
        self.bodyCount: int = 0
        self.bodies: SparseList = []

    def _filepath(self,systemAddress:int):
        filename=f'{systemAddress:016x}.json'
        return f'{self.datadir}/{filename[0:2]}/{filename[3:5]}/{filename}'

    def _child_to_parents(self,body) -> None:
        """
        Parent info from a scan is a list of ordered dictionaries, starting
        with the direct parent, then parent's parent etc. Annoyingly, each
        parent is in a dict, with type of parent as the key and the bodyid
        as the value.  If we don't already have the parent(s) in the tree
        we'll add placeholders
        """
        if body.get("parents"):
            childId=body['bodyId']
            for parent in body['parents']:
                for bodytype,parentId in parent.items():
                    if self.bodies[parentId]!=None:
                        if self.bodies[parentId].get("children"):
                            self.bodies[parentId]["children"].append(childId)
                        else:
                            self.bodies[parentId]["children"]=list([childId])
                    else:
                        self.bodies[parentId]={"type":bodytype,"children":list([childId])}
                    self.bodies[childId]["parentId"]=parentId
                    childId=parentId
        else:
            self.bodies[body['bodyId']]['parentId']=0
        return
