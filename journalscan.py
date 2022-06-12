
def scan_to_body(scan:dict,body:dict) -> dict:
    # take a scan, return updated body

    # Most stuff can simply be renamed
    for jnl, sys in SCAN_RENAMES.items():
        if scan.get(jnl):
            body[sys]=scan.get(jnl)
    # determine type
    if scan.get("StarType"):
        body["type"]="star"
        # map journal name to short name
        body["subType"]=SCAN_STARTYPES[scan.get("StarType")]
        # infer scoopability?
    elif scan.get("PlanetClass"):
        body["type"]="planet"
        body["subType"]=SCAN_PLANETTYPES[scan.get("PlanetClass")]
    else:
        body["type"]="null"
    if scan.get("AtmosphereType"):
        body["atmosphereType"]=SCAN_ATMOTYPES[scan.get("AtmosphereType")]
    if scan.get("Volcanism"):
        body["volcanism"]=SCAN_VOLCANISM[scan.get("Volcanism")]
    if scan.get("SurfaceGravity"):
        body["gravity"]=scan.get("SurfaceGravity")/SCAN_G
    if scan.get("SurfacePressure"):
        # Convert from millibar 
        body["surfacePressure"]=scan.get("SurfacePressure")*SCAN_MBAR_TO_ATM
    return body

def bodysignals(fsssignals:dict,body:dict) -> dict:
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
        "WasMapped":"mapped",
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
        "Gas giant with water-based life":"GG WL",
        "Gas giant with ammonia-based life":"GG AL",
        "Sudarsky Class I gas giant":"GG I",
        "Sudarsky Class II gas giant":"GG II",
        "Sudarsky Class III gas giant":"GG III",
        "Sudarsky Class IV gas giant":"GG IV",
        "Sudarsky Class V gas giant":"GG V",
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
        "Nitrogen":"N",
        "WaterRich":"H\u2082O*",
        "MethaneRich":"CH\u2084*",
        "AmmoniaRich":"NH\u2083*",
        "CarbonDioxideRich":"CO\u2082*",
        "Methane":"CH\u2084",
        "Helium":"He",
        "SilicateVapour":"Si",
        "MetallicVapour":"Me",
        "NeonRich":"Ne*",
        "ArgonRich":"Ar*",
        "Neon":"Ne",
        "Argon":"Ar",
        "Oxygen":"O",
        "NitrogenRich":"N*"
        }
