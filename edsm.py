import json
import logging
import os
from SparseList import SparseList
import timeout_session
from typing import Optional, Dict, Any
from config import appname

plugin_name=os.path.basename(os.path.dirname(__file__))
logger=logging.getLogger(f'{appname}.{plugin_name}')

def getsystem(systemAddress:int) -> (SparseList,int):
    session=timeout_session.new_session()
    r=session.get(f'https://www.edsm.net/api-system-v1/bodies?systemId64={systemAddress}')
    r.raise_for_status()
    edsm=r.json()

    if edsm['id64'] != systemAddress:
        raise Exception("EDSM didn't give us the system we asked for")

    bodies=SparseList()
    for body in edsm.get("bodies"):
        body['discovered']=True
        if 'solarRadius' in body.keys():
            body['radius']=body['solarRadius']*EDSM_SOLARRADIUS
        elif 'radius' in body.keys():
            body['radius']=body['radius']*1000
        if body.get('subType') in EDSM_SUBTYPES:
            body['subType']=EDSM_SUBTYPES[body['subType']]
        elif boty.get('subType'):
            logger.info(f'Unknown subtype: {body["subType"]}')
        # might have to trim off hot/cold thick/thin here
        if body.get('atmosphereType'):
            body['atmosphereType']=body['atmosphereType'].replace("Thick ","").replace("Thin ","").replace("Hot ","")
        if body.get('atmosphereType') in EDSM_ATMOTYPES:
            body['atmosphereType']=EDSM_ATMOTYPES[body['atmosphereType']]
        elif body.get('atmosphereType'):
            logger.info(f'Unknown atmosphere type: {body["atmosphereType"]}')
        if 'belt' in body.keys():
            body['rings']=body.pop('belt')
        if body.get('isScoopable')==True:
            body['actions']="Scoop"
        elif body.get('isLandable')==True:
            body['actions']="Land"
        body['discovered']=True # If it's in EDSM...
        body['scanType']="EDSM"
        body['systemAddress']=edsm['id64']
        body['mapped']="unknown"
        bodies[body['bodyId']]=body
    return (bodies,edsm['bodyCount'])


EDSM_SUBTYPES={
        "O (Blue-White) Star":"*O*",
        "B (Blue-White) Star":"*B*",
        "B (Blue-White super giant) Star":"**B**",
        "A (Blue-White) Star":"*A*",
        "A (Blue-White super giant) Star":"**A**",
        "F (White) Star":"*F*",
        "F (White super giant) Star":"**F**",
        "G (White-Yellow) Star":"*G*",
        "G (White-Yellow super giant) Star":"**G**",
        "K (Yellow-Orange) Star":"*K*",
        "K (Yellow-Orange giant) Star":"+*K*+",
        "M (Red dwarf) Star": "*M*",
        "M (Red giant) Star": "+*M*+",
        "M (Red super giant) Star":"**M**",
        "L (Brown dwarf) Star":"*L*",
        "T (Brown dwarf) Star":"*T*",
        "Y (Brown dwarf) Star":"*Y*",
        "T Tauri Star":"*TT*",
        "Herbig Ae/Be Star":"*Ae/BG*",
        "Wolf-Rayet Star":"*W*",
        "Wolf-Rayet N Star":"*WN*",
        "Wolf-Rayet NC Star":"*WNC*",
        "Wolf-Rayet C Star":"*WC*",
        "Wolf-Rayet O Star":"*WO*",
        "C Star":"*C*",
        "CN Star":"*CN*",
        "CJ Star":"*CJ*",
        "MS-type Star":"*MS*",
        "S-type Star":"*S*",
        "White Dwarf (D) Star":">D<",
        "White Dwarf (DA) Star":">DA<",
        "White Dwarf (DAB) Star":">DAB<",
        "White Dwarf (DAZ) Star":">DAZ<",
        "White Dwarf (DAV) Star":">DAV<",
        "White Dwarf (DB) Star":">DB<",
        "White Dwarf (DBZ) Star":">DBZ<",
        "White Dwarf (DBV) Star":">DBV<",
        "White Dwarf (DQ) Star":">DQ<",
        "White Dwarf (DC) Star":">DC<",
        "White Dwarf (DCV) Star":">DCV<",
        "Neutron Star":">N<",
        "Black Hole":"(BH)",
        "Supermassive Black Hole":"((BH))",
        "Metal-rich body":"MRB",
        "High metal content world":"HMC",
        "Rocky body":"RB",
        "Rocky Ice world":"RIW",
        "Icy body":"IB",
        "Earth-like world":"ELW",
        "Water world":"WW",
        "Water giant":"WG",
        "Ammonia world":"AW",
        "Gas giant with water-based life":"GG WL",
        "Gas giant with ammonia-based life":"GG AL",
        "Class I gas giant":"GG I",
        "Class II gas giant":"GG II",
        "Class III gas giant":"GG III",
        "Class IV gas giant":"GG IV",
        "Class V gas giant":"GG V",
        "Helium-rich gas giant":"He G",
        "Helium gas giant":"GG He"
        }
EDSM_ATMOTYPES={
        "No atmosphere":"-",
        "Ammonia and Oxygen":"NH\u2083+O",
        "Ammonia":"NH\u2083",
        "Water":"H\u2082O",
        "Carbon dioxide":"CO\u2082",
        "Sulphur dioxide":"SO\u2082",
        "Nitrogen":"N\u2082",
        "Water-rich":"H\u2082O*",
        "Methane-rich":"CH\u2084*",
        "Ammonia-rich":"NH\u2083*",
        "Carbon dioxide-rich":"CO\u2082*",
        "Methane":"CH\u2084",
        "Helium":"He",
        "Silicate vapour":"Si\u2093",
        "Metallic vapour":"Me",
        "Neon-rich":"Ne*",
        "Argon-rich":"Ar*",
        "Neon":"Ne",
        "Argon":"Ar",
        "Oxygen":"O",
        "Nitrogen-rich":"N*"
        }
EDSM_SOLARRADIUS=696340000
