import math
import numpy
'''This set of functions is used to do basic survey math
Find the Radius of earth at you LAT acording to WGS84
Find the second set of LAT LONG given a first lat long, distance, Radius, Bearing
Find
'''


#finds the radius of the earth at the lat given I left the radius DEF
#as a long string so I can debug and see what the outputs are at each step
# simply put a print stament below each to see
def radius (lat1):
    B = (lat1)
    #a = 6378.137 #Radius at sea level at equator
    #b = 6356.752 #Radius at poles
    aWGS = 6378.137  #Radius at sea level at equator in km WGS 84
    bwgs = 6356.7523142   #Radius at poles in km WG84
    c = (aWGS**2*math.cos(B))**2
    d = (bwgs**2*math.sin(B))**2
    e = (aWGS*math.cos(B))**2
    f = (bwgs*math.sin(B))**2
    R = math.sqrt((c+d)/(e+f)) #return the radius in KM!!!
    return float(R)
def scale_distance_reality(paperdistance, scale):
    distance = float(paperdistance*scale)
    return float(distance)

def scale_distance_paper(realdistance,scale):
    distance = realdistance/scale
    return distance
def secondcord(lat1,lon1, radius, distance,brng): #must be in radians
#the math for the lat1 and lon1 to LAT2 and LON2 retun lat2 long2 as radian
    lat2 = math.asin(math.sin(lat1)*math.cos(distance/radius) + math.cos(lat1)*math.sin(distance/radius)*math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(distance/radius)*math.cos(lat1),math.cos(distance/radius)-math.sin(lat1)*math.sin(lat2))
    #lat2 = math.degrees(lat2)
    #lon2 = math.degrees(lon2)
    return(lat2,lon2)

# math for calculating the bearing between a lat long to lat long
#return a float
def true_bearing(longa,lata,longb,latb):
    Ldiff = abs(longa - longb)
    x = math.cos(latb)*math.sin(Ldiff)
    y = math.cos(lata)*math.sin(latb)-math.sin(lata)*math.cos(latb)*math.cos(Ldiff)
    #x = math.cos(math.radians(latb) * math.sin(Ldiff))
    #y = math.cos(math.radians(lata) * math.sin(math.radians(latb) - math.sin(math.radians(lata) * math.cos(math.radians(latb) * math.cos(Ldiff)))))
    brg = math.atan2(x,y) #returns radians
    return brg

def distance(lat1,lon1, lat2, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    # Radius of earth in kilometers.
    r = radius(lat1)
    # calculate the result in KM!!!
    return float(c * r)

def angle_bearing(angle,direction):
    if direction == "west" or "south":
        if  angle>= -90 or anlge <= 90 :
            x =  -1
        elif angle<= -90 or anlge >= 90:
            x = +1
    elif direction == "east" or "north":
        if  angle>= -90 or anlge <= 90 :
            x =  +1
        elif angle<= -90 or anlge >= 90:
            x = -1
    return x
def bearing_corrector(bearing):
    if bearing >= 180:
        x = bearing - 360
    elif bearing < 180:
        x = bearing
    return x





