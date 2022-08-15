import latlongbearingdistance_calc as ll
import math
import pyproj


#law of sins given c  and all anglse a/sinA = b/sinB
#a = c·sin(A)/sin(C)
#b = c·sin(B)/sin(C)   sinde AQ = side AB * sin(A_ABQ)/Sin(A_AQB)

# Point A(lat,long), B(lat,long), C(lat,long)
#test points
A = (36.8562027930419, -76.29394435) #A tree
B = (36.85604345, -76.2936773) #B horse
C = (36.85567235, -76.29381739) #C wall

geodesic = pyproj.Geod(ellps='WGS84') #use of this tool in pyrpoj needed to get a better true azimuth calulator

LA = 15.078 #A-B
RA = 18.959#B-C
direction = "south"
Dis_BA = ll.distance(math.radians(B[0]),math.radians(B[1]),math.radians(A[0]),math.radians(A[1]))
Dis_BC = ll.distance(math.radians(B[0]),math.radians(B[1]),math.radians(C[0]),math.radians(C[1]))
#Ang_BA = ll.true_bearing(math.radians(B[1]),math.radians(B[0]),math.radians(A[1]),math.radians(A[0]))
#Ang_CB = ll.true_bearing(math.radians(C[1]),math.radians(C[0]),math.radians(B[1]),math.radians(B[0]))
print(Dis_BA*1000,Dis_BC*1000)

Ang_BA,back_azimuthab,distanceba = geodesic.inv(B[1], B[0], A[1], A[0])
Ang_CB,back_azimuthbc,distancebc = geodesic.inv(C[1], C[0], B[1], B[0])
print("ranges",Ang_BA,Ang_CB)



A_BCQ2 = 90-RA
A_CQ2B = 180 - (2*A_BCQ2) #A_BCQ = 180-(2*A_BCQ) because A_BCQ and A_QBC are the same
degree_A_BCQ = math.degrees(A_BCQ2)
degree_A_CQB = math.degrees(A_CQ2B)
Dis_CQ2 = Dis_BC*math.sin(math.radians(A_BCQ2))/math.sin(math.radians(A_CQ2B))
Bearing_CQ= Ang_CB + (-A_BCQ2) #WEST of points
Bearing_CQ = Ang_CB +(ll.angle_bearing(Ang_CB,direction)*A_BCQ2) # angle CB + (angle bearing calutor from latlongbearingdist produces a - or + 1 based on direction and input angle)*angle
Bearing_CQ = ll.bearing_corrector(Bearing_CQ) #correct bearing incase it is not int he correct diretion
#Bearing_CQ= Ang_CB +A_BCQ2  East of points
#A_BCQ2-Ang_CB East of points





A_ABQ2 = 90-LA
A_BQ2A = 180 - (2*A_ABQ2)
Dis_BQ2 = Dis_BA*(math.sin(math.radians(A_ABQ2))/math.sin(math.radians(A_BQ2A)))
#Bearing_BQ= Ang_BA + (-A_ABQ2)
Bearing_BQ = Ang_BA +(ll.angle_bearing(Ang_BA,direction)*A_ABQ2)
Bearing_BQ = ll.bearing_corrector(Bearing_BQ)#correct bearing incase it is not int he correct diretion


print("bearings",Bearing_CQ,Bearing_BQ)

print(Dis_CQ2,Bearing_CQ)
point1 = ll.secondcord(math.radians(C[0]),math.radians(C[1]),ll.radius(C[0]),Dis_CQ2,math.radians(Bearing_CQ))
print(math.degrees(point1[0]),math.degrees(point1[1]),Dis_CQ2)



print(Dis_BQ2,Bearing_BQ)
point2 = ll.secondcord(math.radians(B[0]),math.radians(B[1]),ll.radius(B[0]),Dis_BQ2,math.radians(Bearing_BQ))
print("CQ",math.degrees(point1[0]),math.degrees(point1[1]),"Radius of the circle",Dis_CQ2)
print("BQ",math.degrees(point2[0]),math.degrees(point2[1]),"Radius of the circle",Dis_BQ2)
print(Bearing_CQ,Dis_CQ2)
print(Bearing_BQ,Dis_BQ2)



#To build list
# if the three points are lined up N-S and user selects N or S gives user and Error and says why cant do that same for E-W
# buld in Error mesages
# build in error for a Swing cirlce if possible
