"""
Name: Taylor Krabiel
Python: 3.6 Arcpro Enviorment
Assistiance:

"""

"""
Three Point Tool Arcpy is used to find a fix based upon 3 land points Angles
Requires the use of the  latlongbearingdistance_calc and pyproj
latlongbearingdistance_calc and pyproj provide calculations for basic survey math like:
Distance between two points
Angle/bearing between two points (pyproj)
Radius of earth at given longitude
Coordinates of secondary point given bearing, distance, and radius of earth at given Long
Corrections for bearing
Law of Sins used for This Three Point Problem

This tool is intedted to be used in WGS84
All math is done in Radians with input in Degrees
Units are Kilometers (except the depth unit)

Tool Input:
- Three points as shape file
    - Point must be labled A,B,C for FID 0,1,2 respectifully
    - Points must be Left to Right or North to South With A being most left or most north
    -Points must be in LAT LONG
- detph and detph unit (not used) (for users own needs)
- date and time (not used) (for users own needs)
- Left and Right Angle
- Direction: Must be in North, South, East, West
    - This direction represents where the Fix was taken.
    - I.E. If fix was taken South of the orgnial three points user enters "South"
- Working Directory
Output:
Severeral Files are created for the user
The files are given a unique name based on the LA and RA to ensure they are unquie
CSV_P.csv is a collection of all Points and Angles produced as well as the Radius of the circles that
are created to find the final fix
Points.shp are all teh points created
Circle.shp are two circles created based on the imaginary triangle points and the Radius
Fix The final Fix. TWO final Fixas will apear. HOWEVER, the one NOT on the point B is the one you want

The math of this is based upon the Three-Body-Fix math found:
https://www.starpath.com/resources2/secure/library/coastal/three_body_piloting.pdf
https://maritimesa.org/nautical-science-grade-10/2020/12/09/horizontal-sextant-angle-hsa/
https://photolib.noaa.gov/Collections/Coast-Geodetic-Survey/Nautical-Charting/Navigation/3-Point-Sextant-Fix/emodule/986/eitem/46491
Bowditch Practinal Navigation
"""
#import
import latlongbearingdistance_calc as ll
import math
import pyproj
from pyproj import CRS
import arcpy
import os
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
import datetime


def uname(LA, RA):
    unique_name = "_LA" + str(int(LA)) + "_RA" + str(int(RA))
    return unique_name

#errors
# Define Error Handling
class spatialAnalysis(Exception):  # Spatial Analysis must be on
    pass
class directionerr(Exception): #if the direction is not = North, South, East, West
    pass #stop script and raise error
class pointserr(Exception):#Points must be labeled A,B,C for FID 0,1,2 respecfully
    pass
class agreatesterr(Exception): # points must be read right to left or north to south.
    #if points not in this direction raise error
    pass
class zuniterr(Exception): #zunit must be feet, meters, or fathoms. doesnt matter capitolization
    pass
try:
    # Set environment settings
    #inputs

    work = arcpy.GetParameterAsText(0)
    arcpy.env.workspace = work
    arcpy.env.overwriteOutput = True #allow to overwrite
    os.chdir(work)
    Three_Points = arcpy.GetParameterAsText(1)
    fields = ['Point', 'SHAPE@XY']
    point_dic = {}
    with arcpy.da.SearchCursor(Three_Points, fields) as cursor:
        for row in cursor:
            point_dic[ row[ 0 ] ] = row[ 1 ]
    if list(point_dic) == [ 'A', 'B', 'C' ]:
        A = point_dic["A"]
        B = point_dic["B"]
        C = point_dic["C"]
        arcpy.AddMessage("Points in {0} labeled properly\n".format(Three_Points))
    else:
        raise pointserr
    #input for depth
    depth = arcpy.GetParameterAsText(2)
    #input for depth units
    zunit = arcpy.GetParameterAsText(3)
    zunit = zunit.lower()
    zunittest = zunit in ["feet", "meter", "fathoms"]
    if zunittest == True:
        arcpy.AddMessage("Depth united entered: {0}\n".format(zunit))
        pass
    else:
        raise zuniterr
    location = arcpy.GetParameterAsText(4)
    time = arcpy.GetParameterAsText(5)
    date = arcpy.GetParameterAsText(6) #m/d/yyyy
    # input Left Anlge, Input Right Angle. Left=A-B Right=B-C
    # LA = 15.078 #A-B
    # RA = 18.959#B-C
    Left_An = arcpy.GetParameterAsText(7)
    LA = float(Left_An)
    Right_An = arcpy.GetParameterAsText(8)
    RA = float(Right_An)
    direction = arcpy.GetParameterAsText(9)
    #input Direction. Only accept North, South, East, West
    direction = direction.lower()#Use .lower() so that the user users capitolization doesnt matter
    if direction in ["north","south","east","west"]:
        arcpy.AddMessage("Direction {0} entered\n".format(direction))
        pass
    else:
        raise directionerr
    # Test that Spatial Analysis extension is available if not then raise error
    if arcpy.CheckExtension("Spatial") == "Available":
        pass
    else:
        raise spatialAnalysis

    #Lat[1] = Y +/- N/S Long[0] = X +/- E/W
    if A[1] >= 0 and A[0] >= 0: #in North East
        if direction in ["east","west"]:
            A_greater_BC = abs(A[ 1 ]) > abs(B[ 1 ]) and abs(A[ 1 ]) > abs(C[ 1 ])
            if A_greater_BC == True:
                pass
            else:
                raise agreatesterr
        else:
            A_greater_BC =  abs(A[0]) > abs(B[0]) and abs(A[0]) > abs(C[0])
            if A_greater_BC == True:
                pass
            else:
                raise agreatesterr
    if A[1] >= 0  and A[0] < 0: #in the North West
        if direction in ["east","west"]:
            A_greater_BC = abs(A[ 1 ]) > abs(B[ 1 ]) and abs(A[ 1 ]) > abs(C[ 1 ])
            if A_greater_BC == True:
                pass
            else:
                raise agreatesterr
        else:
            A_greater_BC =  abs(A[0]) > abs(B[0]) and abs(A[0]) > abs(C[0])
            if A_greater_BC == True:
                pass
            else:
                raise agreatesterr
    if A[1] < 0  and A[0] < 0: #in the South East
        if direction in ["east","west"]:
            A_greater_BC = abs(A[ 1 ]) < abs(B[ 1 ]) and abs(A[ 1 ]) < abs(C[ 1 ])
            if A_greater_BC == True:
                pass
            else:
                raise agreatesterr
        else:
            A_greater_BC =  abs(A[0]) > abs(B[0]) and abs(A[0]) > abs(C[0])
            if A_greater_BC == True:
                pass
            else:
                raise agreatesterr
    if A[1] < 0 and A[0] < 0: #in the South West
        if direction in [ "east", "west" ]:
            A_greater_BC = abs(A[ 1 ]) < abs(B[ 1 ]) and abs(A[ 1 ]) < abs(C[ 1 ])
            if A_greater_BC == True:
                pass
            else:
                raise agreatesterr
        else:
            A_greater_BC = abs(A[ 0 ]) > abs(B[ 0 ]) and abs(A[ 0 ]) > abs(C[ 0 ])
            if A_greater_BC == True:
                pass
            else:
                raise agreatesterr
    # Find distance from B-A find Distance from B-C
    Dis_BA = ll.distance(math.radians(B[ 1 ]), math.radians(B[ 0 ]), math.radians(A[ 1 ]), math.radians(A[ 0 ]))
    Dis_BC = ll.distance(math.radians(B[ 1 ]), math.radians(B[ 0 ]), math.radians(C[ 1 ]), math.radians(C[ 0 ]))
    geodesic = pyproj.Geod(ellps='WGS84')  # set the geodesic to be the datumn WGS84

    # Find distance from B-A find Distance from B-C
    # find the true azimul from B-A and C-B
    Ang_BA, back_azimuthab, distanceba = geodesic.inv(B[ 0 ], B[ 1 ], A[ 0 ], A[ 1 ])
    Ang_CB, back_azimuthbc, distancebc = geodesic.inv(C[ 0 ], C[ 1 ], B[ 0 ], B[ 1 ])


    # find the true azimul from B-A and C-B
    Ang_BA, back_azimuthab, distanceba = geodesic.inv(B[ 0 ], B[ 1 ], A[ 0 ], A[ 1 ])
    Ang_CB, back_azimuthbc, distancebc = geodesic.inv(C[ 0 ], C[ 1 ], B[ 0 ], B[ 1 ])

    # law of sins given c  and all anglse a/sinA = b/sinB
    # a = c·sin(A)/sin(C)
    # b = c·sin(B)/sin(C)   sinde AQ = side AB * sin(A_ABQ)/Sin(A_AQB)
    #Imagine a Triangle pointed down \/
    # Left-Center-Right
    # Point:A , C, B A\C/B
    # Angles: A_CAB, A_ABC, A_BCA A_CAB\A_ABC/A_BCA
    # MUST HAVE A_ABC and A_CAB  Equal
    def law_of_sins_hydro(Dis_AB,RA_LA): #distance returned in KM
        #fidning point C and Angle A_BCA
        A_ABC = 90 - RA_LA
        A_BCA = 180 - (2 *A_ABC) #only works if ABC and CAB are Equal
        degree_A_ABC = math.degrees(A_ABC)
        degree_A_BCA = math.degrees(A_BCA)
        Dis_BC = Dis_AB * math.sin(math.radians(A_ABC)) / math.sin(math.radians(A_BCA))
        return Dis_BC,A_ABC


    Dis_CQ2 = law_of_sins_hydro(Dis_BC,RA)[0]   # Triangle points are BCQ, point Q is imaginary
    Dis_BQ2 = law_of_sins_hydro(Dis_BA,LA)[0]   # Triangle points are ABQ, point Q is imaginary
    # angle CB + (angle bearing calutor from latlongbearingdist produces a - or + 1 based on direction and input angle)*angle
    # correct bearing incase it is not int he correct diretion
    Bearing_CQ = Ang_CB + (ll.angle_bearing(Ang_CB,direction) * law_of_sins_hydro(Dis_BC,RA)[1])
    Bearing_CQ = ll.bearing_corrector(Bearing_CQ)
    Bearing_BQ = Ang_BA + (ll.angle_bearing(Ang_BA,direction) * law_of_sins_hydro(Dis_BA,LA)[1])
    Bearing_BQ = ll.bearing_corrector(Bearing_BQ)
    # correct bearing incase it is not int he correct diretion
    # convert everything to radians
    pointCQ = ll.secondcord(math.radians(C[ 1 ]), math.radians(C[ 0 ]), ll.radius(C[ 1 ]), Dis_CQ2,
                            math.radians(Bearing_CQ))
    # find the coordinates for point BQ using the lat long of B, the radius of earth at B,the distance from B-Q
    # and the bearing of BQ
    # convert everything to radian
    pointBQ = ll.secondcord(math.radians(B[ 1 ]), math.radians(B[ 0 ]), ll.radius(B[ 1 ]), Dis_BQ2,
                            math.radians(Bearing_BQ))

    # define point CQ&BQ in degrees retrun the radius of the cirlce as Dis_CQ2 and Dis_BQ2
    # distance is in km
    pointCQ = (math.degrees(pointCQ[ 0 ]), math.degrees(pointCQ[ 1 ]))
    pointCQ_radius = Dis_CQ2
    pointBQ = (math.degrees(pointBQ[ 0 ]), math.degrees(pointBQ[ 1 ]))
    pointBQ_radius = Dis_BQ2

    #create files for ARCPY and the user
    File_list = [ "CSV_P" + uname(LA, RA), "Points" + uname(LA, RA), "circles" + uname(LA, RA),
                  "Fix" + "_" + uname(LA, RA) ]
    #Create a CSV for the user
    data = pd.DataFrame([ [ location, "A", A[ 1 ], A[ 0 ], "0 Kilometers", depth, time, date, LA, RA ],
                          [ location, "B", B[ 1 ], B[ 0 ], "0 Kilometers", depth, time, date, LA, RA ],
                          [ location, "C", C[ 1 ], C[ 0 ], "0 Kilometers", depth, time, date, LA, RA ],
                          [ location, "BQ", pointBQ[ 0 ], pointBQ[ 1 ], str(pointBQ_radius) + " Kilometers", depth,
                            time, date, LA, RA ],
                          [ location, "CQ", pointCQ[ 0 ], pointCQ[ 1 ], str(pointCQ_radius) + " Kilometers", depth,
                            time, date, LA, RA ] ],
                        columns=[ "Location", 'Point', 'latitude', 'longitude', 'Radius', 'Depth in ' + str(zunit),
                                  'Local Time', 'Date', "Left Angle", "Right Angle" ])
    data.to_csv(File_list[ 0 ] + ".csv")
    #xytable to points
    arcpy.management.XYTableToPoint(File_list[ 0 ] + ".csv", File_list[ 1 ],
                                    "longitude", "latitude")
    arcpy.analysis.Buffer(File_list[1] + ".shp", File_list[2], "Radius", "FULL", "ROUND")

    arcpy.analysis.Intersect(File_list[ 2 ] + ".shp", File_list[ 3 ], "", "", "point")

    arcpy.AddMessage("\nThe following files have been created: CSV of All Values = {0} \n "
                     "Orginal Three Points and Two Q points = {1}\n "
                     "Two Cirlces from Q points = {2}\n "
                     "and Your Final Fix = {3} \n"
                     "files are located here: {4}"
                     .format(File_list[ 0 ],
                             File_list[ 1 ],
                             File_list[ 2 ],
                             File_list[ 3 ],
                             work))
    test_swing = min(round(Dis_BA * 1000, 0), round(Dis_BC * 1000, 0)) + 5 >= max(round(Dis_BA * 1000, 0),
                                                                                  round(Dis_BC * 1000, 0))
    if test_swing == False: #round to the nearest meter
        pass
    else:
        #If the swinger cirlce exsists plot this information as well
        arcpy.AddError("The three points used exists within a Swinger. "
                       "The three points are within 5 meters of the same distance of eachother."
                       "A Swinger_Circle has been produced for your conviance.")
        # plot point BQ_Swing
        BQ_Swing = ll.secondcord(math.radians(B[1]),math.radians(B[0]),ll.radius(B[1]),Dis_BC,math.radians(180))
        Swing = pd.DataFrame([[location,"A",A[1],A[0],
                               "0 Kilometers",depth,time,date,LA,RA],
                              [location,"B",B[1],B[0],"0 Kilometers",depth,time,date,LA,RA],
                              [location,"C",C[1],C[0],"0 Kilometers",depth,time,date,LA,RA],
                              [location,"BQ_Swinger",BQ_Swing[0],
                               BQ_Swing[1],str(Dis_BC)+" Kilometers",depth,time,date,LA,RA]]
                             , columns=["Location",'Point','latitude',
                                        'longitude','Radius','Depth in '+str(zunit),'Local Time',
                                        'Date',"Left Angle","Right Angle"])
        Swing.to_csv('swinger.csv')
        arcpy.management.XYTableToPoint("swinger.csv", "Swinger","longitude", "latitude")
        arcpy.analysis.Buffer("Swinger.shp", "Swinger_circle", "Radius", "FULL", "ROUND")
#TESTING PRINTS
# print(Dis_BA*1000,Dis_BC*1000)
# print(Dis_BA*1000,Dis_BC*1000)
# print("ranges",Ang_BA,Ang_CB)
# print("bearings",Bearing_CQ,Bearing_BQ)
# print(Dis_CQ2,Bearing_CQ)
# print(math.degrees(pointCQ[0]),math.degrees(pointCQ[1]),Dis_CQ2)

# print(Dis_BQ2,Bearing_BQ)
# print("CQ",math.degrees(pointCQ[0]),math.degrees(pointCQ[1]),"Radius of the circle",Dis_CQ2)
# print("BQ",math.degrees(pointBQ[0]),math.degrees(pointBQ[1]),"Radius of the circle",Dis_BQ2)
# print(Bearing_CQ,Dis_CQ2)
# print(Bearing_BQ,Dis_BQ2)



except spatialAnalysis:
    arcpy.AddError('Spatial Analysis Extension Is Not Available')
except directionerr:
    arcpy.AddError("Direction {0} entered. Only North, South, East, West accepted.".format(direction))
except pointserr:
    arcpy.AddError("The points in file {0} are not properly labled A,B,C from OID 0,1,2".format(Three_Points))
except agreatesterr:
    arcpy.AddError("This tool requires the points A,B,C to be Left to Right, or North to South. "
                   "Your Point A is either Right of Point B or C, or Point A is South of Point B or C")
except zuniterr:
    arcpy.AddError("Depth united entered: {0} "
                   "Only accepted units are: Feet, Fathom, Meters".format(zunit))
    # Buffer
    # arcpy.analysis.Buffer(in_features, out_feature_class, buffer_distance_or_field, {line_side}, {line_end_type}, {dissolve_option}, {dissolve_field}, {method})
    # output
    # buffer_circles = ""
    # input =
    # left_right_buffers = "C:/output/Output.gdb/buffer_output"
    # distanceField = "Radius_KM"
    # sideType = "FULL"
    # endType = "ROUND"
    # arcpy.analysis.Buffer(input, left_right_buffers, distanceField, sideType, endType, dissolveType, dissolveField)

    """#buffer with geopandas
    def point_buffer(point, radius):

        x = gpd.GeoSeries(Point(point))
        #x = x.set_crs("EPSG:4326")
        buff = x.buffer(radius)
        return buff

    print(point_buffer(pointCQ,pointCQ_radius))
    buff1 = point_buffer(pointCQ,pointCQ_radius)
    #buff1 = buff1.to_crs(epsg=4326)
    buff1.to_file("countries.geojson", driver='GeoJSON')
    print(buff1.crs is None)
    #CRS("EPSG:4326")

    def intersects(polya,polyb):
        points = polya.insterects(polyb)
        return points"""
'''Leggacy code to understand what is happending with the law_of_sins_hydro calulator
    Create Triangle for RA
    A_BCQ2 = 90 - RA
    A_CQ2B = 180 - (2 * A_BCQ2)  # A_BCQ = 180-(2*A_BCQ) because A_BCQ and A_QBC are the same
    degree_A_BCQ = math.degrees(A_BCQ2)
    degree_A_CQB = math.degrees(A_CQ2B)
    Dis_CQ2 = Dis_BC * math.sin(math.radians(A_BCQ2)) / math.sin(math.radians(A_CQ2B))
    Create Triangle for LA
    A_ABQ2 = 90 - LA
    A_BQ2A = 180 - (2 * A_ABQ2)
    Dis_BQ2 = Dis_BA * (math.sin(math.radians(A_ABQ2)) / math.sin(math.radians(A_BQ2A)))
    find the coordinates for point CQ using the lat long of C, 
    the radius of earth at C,the distance from C-Q
    and the bearing of CQ'''