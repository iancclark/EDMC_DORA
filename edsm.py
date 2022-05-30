import json
import logging
import os
import SparseList
import timeout_session
from typing import Optional, Dict, Any


def getsystem(systemAddress:int) -> (SparseList,int):
    session=timeout_session.new_session()
    r=session.get(f'https://www.edsm.net/api-system-v1/bodies?systemId64={systemAddress}')
    r.raise_for_status()
    edsm=r.json()

    if edsm['id64'] != systemAddress:
        raise Exception("EDSM didn't give us the system we asked for")

    bodies: SparseList=[]
    for body in edsm.get(bodies):
        body: dict = {discovered:True}
        if 'solarRadius' in body.keys():
            body['solarRadius']=body['solarRadius']*EDSM_SOLARRADIUS
        if body.get('atmosphereType') in EDSM_ATMOTYPES:
            body['atmosphereType']=EDSM_ATMOTYPES[body['atmosphereType']]
        if body.get('subType') in EDSM_SUBTYPES:
            body['subType']=EDSM_SUBTYPES[body['subType']]
        if body.get('atmosphereType') in EDSM_ATMOTYPES:
            body['atmosphereType']=EDSM_ATMOTYPES[body['atmosphereType']]
        if 'radius' in body.keys():
            body['radius']=body['radius']*1000
        if 'belt' in body.keys():
            body['rings']=body.pop('belt')
        body['discovered']=True
        body['systemAddress']=edsm['id64']
        bodies[body['bodyId']]=body
    return (bodies,edsm['bodyCount'])


EDSM_SUBTYPES={
        "M (Red dwarf) Star": "*M*",
        "High metal content world":"HMC",
        "Rocky body":"RB",
        "Rocky Ice world":"RIW",
        "Class II gas giant":"GG II"
        }
EDSM_ATMOTYPES={
        "No atmosphere":"-",
        "Argon":"Ar",
        "Thick Argon-rich":"Ar*",
        }
EDSM_SOLARRADIUS=696340000
