"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#

# Putting globals at the top of the file so theyre easy to edit. These to be in a config but eh

start_control_hour_shift = 1

max_brevet_distance_multiple = 1.20

brevet_max_times_shift = [(200, 10), (400, 20)]

control_speedlimits = [(1000, 13.333, 26), (600, 11.428, 28), (400, 15, 30), (300, 15, 32), (200, 15, 32), (0, 15, 34)]

def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    #Stop and returns false if we're out of bounds
    if int(control_dist_km) > brevet_dist_km * max_brevet_distance_multiple:
        return False
    
    #set control dist to brev distance if within acceptable bounds of final control 
    control_dist_km = getControlDist(control_dist_km, brevet_dist_km)
    
    #loop to calculate hour value and successively decrease control distance to change speed limits
    base_hours = 0
    for dist, minspeed, maxspeed in control_speedlimits:
        base_hours = calcHoursVals(control_dist_km, dist, maxspeed, base_hours)
  
    #Our time formatting broke a little, had to change it back t ISO
    return arrow.get(brevet_start_time).shift(hours=base_hours).isoformat()

def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    #Control 1
    closetime = arrow.get(brevet_start_time)
    if control_dist_km == 0:
        return closetime.shift(hours=start_control_hour_shift).isoformat()
    
    #Get control dist
    control_dist_km = getControlDist(control_dist_km, brevet_dist_km)
    
    #Set close time
    closetime = getCloseTime(control_dist_km, closetime)
 
    #loop to change hours multiple and speed limits 
    converted_hours = convertHours(control_dist_km)
    return closetime.shift(hours=converted_hours).isoformat()

################
#
#Helper methods are the bottom so thier values are defined
#
###########

#Helper method to convert some hour data
def convertHours(control_dist_km):
    hours = 0
    for dist, minspeed, maxspeed in control_speedlimits:
        hours = calcHoursVals(control_dist_km, dist, minspeed, hours)
    return hours

#Helper method to get our close time
def getCloseTime(control_dist_km, closetime):
    for brevdist, minshift in brevet_max_times_shift:
        if int(control_dist_km) == brevdist:
            closetime = closetime.shift(minutes=minshift)
    return closetime

#helper method to get or control distance
def getControlDist(control_dist_km, brevet_dist_km):
    if (int(control_dist_km) <= brevet_dist_km * max_brevet_distance_multiple and int(control_dist_km) > brevet_dist_km):
        control_dist_km = brevet_dist_km
    return control_dist_km

#Calculate the new values with speed and max speed and dist
def calcHoursVals(control_dist_km, dist, maxspeed, base_hours):
    if control_dist_km > dist:
        base_hours += (control_dist_km - dist) / maxspeed
        control_dist_km = dist
    return base_hours
