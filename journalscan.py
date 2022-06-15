import logging
import os
from config import appname

plugin_name=os.path.basename(os.path.dirname(__file__))
logger=logging.getLogger(f'{appname}.{plugin_name}')

def scan_to_body(scan:dict,body:dict) -> dict:
    # take a scan, return updated body

    # Most stuff can simply be renamed
    for jnl, sys in SCAN_RENAMES.items():
        if scan.get(jnl):
            body[sys]=scan.get(jnl)
    # determine type
    if scan.get("StarType") in SCAN_STARTYPES:
        body["type"]="Star"
        # map journal name to short name
        body["subType"]=SCAN_STARTYPES[scan.get("StarType")]
    elif scan.get("StarType"):
        body["type"]="Star"
        logger.info(f"Unknown StarType: {scan['StarType']}")
    elif scan.get("PlanetClass") in SCAN_PLANETTYPES:
        body["type"]="Planet"
        body["subType"]=SCAN_PLANETTYPES[scan.get("PlanetClass")]
    elif scan.get("PlanetClass"):
        body["type"]="Planet"
        logger.info(f"Unknown PlanetClass: {scan['PlanetClass']}")
    else:
        body["type"]="Null"
    if scan.get("AtmosphereType"):
        body["atmosphereType"]=SCAN_ATMOTYPES[scan.get("AtmosphereType")]
    elif scan.get("AtmosphereType"):
        logger.info(f"Unknown AtmosphereType type: {scan['AtmosphereType']}")
    if scan.get("Volcanism") in SCAN_VOLCANISM:
        body["volcanism"]=SCAN_VOLCANISM[scan.get("Volcanism").replace(('Major','Minor','Volcanism'),('','',''))]
    elif scan.get("Volcanism"):
        logger.info(f"Unknown volcanism type: {scan['Volcanism']}")
    if scan.get("SurfaceGravity"):
        body["gravity"]=scan.get("SurfaceGravity")/SCAN_G
    if scan.get("SurfacePressure"):
        # Convert from millibar 
        body["surfacePressure"]=scan.get("SurfacePressure")*SCAN_MBAR_TO_ATM
    if scan.get('StarType') and scan.get('StarType').startswith(('O','B','A','F','G','K','M')):
        body['actions']="Scoop"
    elif scan.get("Landable") == True:
        body['actions']="Land"
    if scan.get("WasMapped") == True and not body.get("mapped"):
        body['mapped']="other"
    return body

def bodysignals(fsssignals:list,body:dict) -> dict:
    # update a body with signal info
    for signal in fsssignals:
        if signal.get("Type") == "$SAA_SignalType_Biological;":
            body['bioSignals']=signal.get("Count")
        elif signal.get("Type") == "$SAA_SignalType_Geological;":
            body['geoSignals']=signal.get("Count")
    return body

SCAN_RENAMES={
        "BodyName": "name",
        "BodyID":"bodyId",
        "Parents":"parents",
        "SystemAddress":"systemAddress",
        "DistanceFromArrivalLS":"distanceToArrival",
        "SurfaceTemperature":"surfaceTemperature",
        "SemiMajorAxis":"semiMajorAxis",
        "Eccentricity":"eccentricity",
        "OrbitalInclination":"orbitalInclination",
        "Periapsis":"argOfPeriapsis",
        "OrbitalPeriod":"orbitalPeriod",
        "AscendingNode":"ascendingNode",
        "MeanAnomaly":"meanAnomaly",
        "RotationPeriod":"rotationalPeriod",
        "Rings":"rings",
        "WasDiscovered":"discovered",
        "AxialTilt":"axialTilt",
        "StellarMass":"solarMasses",
        "Radius":"radius",
        "Age_MY":"age",
        "Luminosity":"luminosity",
        "TidalLock":"rotationalPeriodTidallyLocked",
        "TerraformState":"terraformingState",
        "AtmosphereComposition":"atmosphereComposition",
        "MassEM":"earthMasses",
        "Landable":"isLandable",
        "Composition":"solidComposition",
        "ScanType":"scanType"}
SCAN_G=9.81
SCAN_MBAR_TO_ATM=0.000986923
SCAN_STARTYPES={
        "O":"*O*",
        "B":"*B*",
        "B (Blue-White super giant) Star":"**B**", # Sigma Serpentis
        "A":"*A*",
        "A_BlueWhiteSuperGiant":"**A**",
        "F":"*F*",
        "F_WhiteSuperGiant":"**F**",
        "G":"*G*",
        "G (White-Yellow super giant) Star":"**G**", # Rho Puppis 
        "K":"*K*",
        "K_OrangeGiant":"+*K*+",
        "M": "*M*",
        "M_RedGiant": "+*M*+",
        "M_RedSuperGiant":"**M**",
        "L":"*L*",
        "T":"*T*",
        "Y":"*Y*",
        "TTS":"*TT*",
        "AeBe":"*Ae/BG*",
        "W":"*W*",
        "WN":"*WN*",
        "WNC":"*WNC*",
        "WC":"*WC*",
        "WO":"*WO*",
        "C":"*C*",
        "CS":"*CS*",
        "CN":"*CN*",
        "CJ":"*CJ*",
        "CH":"*CH*",
        "CHd":"*CHd*",
        "MS":"*MS*",
        "S":"*S*",
        "D":">D<",
        "DA":">DA<",
        "DAB":">DAB<",
        "DAZ":">DAZ<",
        "DAV":">DAV<",
        "DB":">DB<",
        "DBZ":">DBZ<",
        "DBV":">DBV<",
        "DQ":">DQ<",
        "DC":">DC<",
        "DCV":">DCV<",
        "N":">N<",
        "H":"(BH)",
        "SupermassiveBlackHole":"((BH))",
        "X":"*X*",
        "RoguePlanet":"RP?",
        "Nebula":")N(",
        "StellarRemnantNebula":")SRN("
        }
SCAN_PLANETTYPES={
        "Metal rich body":"MRB",
        "High metal content body":"HMC",
        "Rocky body":"RB",
        "Rocky ice body":"RIW",
        "Icy body":"IB",
        "Earthlike body":"ELW",
        "Water world":"WW",
        "Water giant":"WG",
        "Ammonia world":"AW",
        "Gas giant with water based life":"GG WL",
        "Gas giant with ammonia based life":"GG AL",
        "Sudarsky class I gas giant":"GG I",
        "Sudarsky class II gas giant":"GG II",
        "Sudarsky class III gas giant":"GG III",
        "Sudarsky class IV gas giant":"GG IV",
        "Sudarsky class V gas giant":"GG V",
        "Helium rich gas giant":"He G",
        "Helium gas giant":"GG He"
 }
SCAN_ATMOTYPES={
        "None":"-",
        "AmmoniaOxygen":"NH\u2083+O",
        "Ammonia":"NH\u2083",
        "Water":"H\u2082O",
        "CarbonDioxide":"CO\u2082",
        "SulphurDioxide":"SO\u2082",
        "Nitrogen":"N\u2082",
        "WaterRich":"H\u2082O*",
        "MethaneRich":"CH\u2084*",
        "AmmoniaRich":"NH\u2083*",
        "CarbonDioxideRich":"CO\u2082*",
        "Methane":"CH\u2084",
        "Helium":"He",
        "SilicateVapour":"SiO\u2093",
        "MetallicVapour":"Me",
        "NeonRich":"Ne*",
        "ArgonRich":"Ar*",
        "Neon":"Ne",
        "Argon":"Ar",
        "Oxygen":"O",
        "NitrogenRich":"N*"
        }

SCAN_VOLCANISM={
        "Water Magma":"H\u2082O \u0466",
        "Sulphur Dioxide Magma":"SO\u2082 \u0466",
        "Ammonia Magma":"NH\u2083 \u0466",
        "Methane Magma":"CH\u2084 \u0466",
        "Nitrogen Magma":"N\u2082 \u0466",
        "Silicate Magma":"SiO\u2093 \u0466",
        "Metallic Magma":"Me \u0466",
        "Water Geysers":"H\u2082O \u0373",
        "Carbon Dioxide Geysers":"CO\u2082 \u0373",
        "Ammonia Geysers":"NH\u2083 \u0373",
        "Methane Geysers":"CH\u2084 \u0373",
        "Nitrogen Geysers":"N\u2082 \u0373",
        "Helium Geysers":"He \u0373",
        "Silicate Vapour Geysers":"SiO\u2093 \u0373"
        }
