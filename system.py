import json
import logging
import os
from typing import Optional, Dict, Any
from SparseList import SparseList
import edsm
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
        return self

    def from_edsm(self,systemAddress:int):
        if self.systemAddress !=0 and self.systemAddress != systemAddress:
            raise Exception("Asked to load data from EDSM when I have some data")
        # should already know systemname/address
        (self.bodyCount,self.bodies)=edsm.getsystem(systemAddress)

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
        with open(_filepath(systemAddress),'w') as f:
            json.dump(self.__dict__,f)
    def body_from_scan(self,data):
        if(data.get("systemAddress") != self.systemAddress):
            raise Exception(f'Received a scan for a different system')
        return
    def body_from_fsssignals(self,data):
        return
    def system_from_fsdjump(self,data):
        # or carrierjump or location 
        return
    def system_from_fsshonk(self,data):
        return
    def body_from_dssscan(self,data):
        return

    def knownbodies(self)->list:
        return [bodies for body in self.bodies if body != None ]

    def _filepath(self,systemAddress:int):
        filename=f'{systemAddress:016x}.json'
        return f'{this.datadir}/{filename[0:2]}/{filename[3:4]}/{filename}'

