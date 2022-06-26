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
        self.bodies= SparseList()
        self.datadir=f'{os.path.dirname(__file__)}/data'
        self.saved=True
        try:
            with open(f'{self.datadir}/lastsystem','r') as f:
                self.systemAddress=int(f.read())
                self.from_file(self.systemAddress)
        except FileNotFoundError:
            logger.warn("No system saved from previous run")
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
        self.saved=False
        return

    def from_file(self,systemAddress:int):
        if self.systemAddress !=0 and self.systemAddress != systemAddress:
            raise Exception("Asked to load data from file when I have some data")
        try:
            with open(self._filepath(systemAddress),'r') as f:
                self.__dict__=json.load(f)
            self.saved=True
            self.datadir=f'{os.path.dirname(__file__)}/data'
        except json.decoder.JSONDecodeError:
            logger.warn("Corrupt datafile")
        return

    def to_file(self):
        if self.saved:
            return
        # make the dir
        savefile=self._filepath(self.systemAddress)

        os.makedirs(os.path.dirname(savefile),exist_ok=True)
        # in case the write gets interrupted for some reason
        # write to a temporary file
        with open(savefile+".tmp",'w') as f:
            json.dump({k:v for k,v in self.__dict__.items() if k not in ('timer','datadir','saved')},f)
        # and rotate.
        os.replace(savefile+".tmp",savefile)
        self.saved=True

    def scan(self,data):
        self.saved=False
        if self.systemAddress==0:
            self.systemAddress=data.get("SystemAddress")
            self.systemName=data['StarSystem']
            # Try to restore from a save file
            try:
                self.from_file(data['SystemAddress'])
            except FileNotFoundError:
                # presumably the file is missing, try EDSM
                self.from_edsm(data['SystemAddress'])
        if(data.get("SystemAddress") != self.systemAddress):
            raise Exception(f'Received a scan for a different system')
        # create body by bodyid if necessary
        body=self.bodies[data['BodyID']]
        if body==None:
            body={"bodyId":data['BodyID']}
        # call scan_to_body from journalscan.py
        body=journalscan.scan_to_body(data,body)
        self.bodies[data['BodyID']]=body
        self._child_to_parents(body)
        return

    def fsssignals(self,data):
        self.saved=False
        # find the appropriate body, pass onto journalscan.py bodysignals
        body=self.bodies[data['BodyID']]
        if body==None:
            body={"bodyId":data['BodyID']}
        body=journalscan.bodysignals(data.get('Signals'),body)
        self.bodies[data['BodyID']]=body
        return

    def fsdjump(self,data):
        # or carrierjump or location 
        # If we have data, and systemAddress different, rotate.
        if self.systemAddress != data['SystemAddress']:
            self.rotate()
            self.systemAddress=data['SystemAddress']
            self.systemName=data['StarSystem']
            self.saved=False

        # Try to restore from a save file
        try:
            self.from_file(data['SystemAddress'])
            self.saved=True
        except FileNotFoundError:
            # presumably the file is missing, try EDSM
            self.from_edsm(data['SystemAddress'])
        # Otherwise just the bare minimum, need a honk for more
        return

    def fsshonk(self,data):
        if self.systemAddress==0:
            self.systemAddress=data.get("SystemAddress")
            self.systemName=data['SystemName']
            # Try to restore from a save file
            try:
                self.from_file(data['SystemAddress'])
            except FileNotFoundError:
                # presumably the file is missing, try EDSM
                self.from_edsm(data['SystemAddress'])
        if data.get("SystemAddress") != self.systemAddress:
            raise Exception(f'Received a scan for a different system')
        # As above, fill in bodyCount
        self.bodyCount=data['BodyCount']
        return

    def dssscan(self,data):
        # get body id, set to mapped
        logger.info(f'dssscan: {data}')
        self.bodies[data['BodyID']]["mapped"]='self'
        self.saved=False
        return

    def knownbodies(self)->list:
        return [body for body in self.bodies if body != None ]

    def systemname(self)->str:
        return self.systemName

    def getBodyCount(self)->int:
        return self.bodyCount

    def rotate(self)->None:
        # save data
        if self.systemAddress != 0:
            self.to_file()
        # clear data
        self.systemAddress: int = 0
        self.systemName: str = ""
        self.bodyCount: int = 0
        self.bodies=SparseList()

    def _filepath(self,systemAddress:int):
        filename=f'{systemAddress:016x}.json'
        return f'{self.datadir}/{filename[0:4]}/{filename[4:8]}/{filename}'

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
                    self.bodies[childId]['parentId']=parentId
                    if self.bodies[parentId]!=None:
                        if self.bodies[parentId].get("children"):
                            self.bodies[parentId]["children"].add(childId)
                        else:
                            self.bodies[parentId]["children"]=set([childId])
                    else:
                        self.bodies[parentId]={"type":bodytype,"bodyId":parentId,"children":set([childId])}
                    childId=parentId
        else:
            self.bodies[body['bodyId']]['parentId']=0
        return  

    def shut(self):
        if self.systemAddress != 0:
            self.to_file();
            with open(f'{self.data}/lastsystem','w') as f:
                f.write(str(self.systemAddress))
