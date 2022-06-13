Journal Scan            EDSM                            DORA                    Notes
------------            ----                            ----                    -----
BodyName                name                            name                    Rename needed from journal
BodyID                  bodyId                          bodyId			Rename needed from journal
Parents                 parents                         parents                 List of k:v where k is type and v is bodyid, maybe make a tree?
StarSystem              -                               - (systemName 1 lvlup)  Move up a level
SystemAddress           - (id64 one level up)           systemAddress           Also copy up a level for journal
DistanceFromArrivalLS   distanceToArrival               distanceToArrival       Rename needed from journal
SurfaceTemperature      surfaceTemperature              surfaceTemperature      Rename needed from journal
SemiMajorAxis           semiMajorAxis                   semiMajorAxis           Rename needed from journal
Eccentricity            orbitalEccentricity             orbitalEccentricity     Rename needed from journal
OrbitalInclination      orbitalInclination              orbitalInclination      Rename needed from journal
Periapsis               argOfPeriapsis                  argOfPeriapsis          Rename needed from journal
OrbitalPeriod           orbitalPeriod                   orbitalPeriod           Rename needed from journal
AscendingNode           -                               ascendingNode           Rename needed from journal
MeanAnomaly             -                               meanAnomaly             Rename needed from journal (presumably varies over time?)
RotationPeriod          rotationalPeriod                rotationalPeriod        Rename needed from journal
Rings[]                 belts[]                         rings                   Rename needed from both \o/
WasDiscovered           discovery                       discovered              Can be wrong for "pre-discovered" systems, rename needed.
WasMapped               -                               mapped                  Rename needed from journal
AxialTilt               axialTilt                       axialTilt               Rename needed from journal
-                       type                            type                    ring,star,planet,null. Can be infered from other journal fields

StarType                subType (~wording)              subtype (shortened)     Mapping needed from both
StellarMass             solarMasses                     solarMasses             Rename needed from journal
Radius (m)              solarRadius (suns, 696340000m)  radius             	Rename needed from journal, scaling needed from EDSM
Age_MY                  age                             age                     Rename needed from journal
Luminosity              luminosity                      luminosity              Rename needed from journal
-                       isScoopable                     isScoopable             Journal: need to infer from StarType

TidalLock               rotationalPeriodTidallyLocked   rotationalPeriodTidallyLocked
                                                                                Rename needed from journal
TerraformState          terraformingState               terraformingState       Rename needed from journal
PlanetClass             subType (~wording)              subtype (shortened)     Mapping needed from both
Atmosphere              atmosphereType (~wording)       atmosphereType (short)  Mapping needed from both
AtmosphereType          -                               atmosphereType (short)  Mapping needed from both
AtmosphereComposition[] atmosphereComposition{}         atmosphereComposition{} Rename needed from journal
Volcanism               volcanism                       volcanism (short)       Mapping needed from both
MassEM                  eathMasses                      earthMasses             Rename needed from journal
Radius (m?)             radius (km?)                    radius (m)              Rename needed from journal. Mapping needed from EDSM
SurfaceGravity (m/s2)   gravity (g)                     gravity (g)             Journal rename and /9.81
SurfacePressure (mBar)  surfacePressure (atm)           surfacePressure (atm)   Need to check the units here
Landable                isLandable                      isLandable              Rename needed from journal
Composition{}           solidComposition{}              solidComposition        Rename needed from journal
-			-				bioSignals		From FSSBodySignals
-			-				geoSignals		From FSSBodySignals
-			-				actions			Infer from isLandable/isScoopable and journal equivs

Detailed and Orbital Reconaissance Assistant
