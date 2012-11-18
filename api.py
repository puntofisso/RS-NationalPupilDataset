#!/usr/bin/python
# -*- coding: utf-8 -*-
# by Giuseppe Sollazzo @puntofisso

import MySQLdb as mdb
import MySQLdb.cursors
import sys
import json
import re
import string
import math
con = None


#ks4grade = {'FG':0,'GG':0,'DE':0,'EE':0,'EF':0,'**':0,'CC':0,'DD':0,'BB':0,'CD':0,'FF':0,'*A':0,'AA':0,'AB':0,'BC':0,'P':0,'Q':0,'U':0,'*':8,'A':7,'B':6,'C':5,'D':4,'E':3,'F':2,'G':1}
#ks5grade = {'*':300,'A':270,'B':240,'C':210,'D':180,'E':150,'Q':0,'U':0,'X':0}

# distance by http://www.johndcook.com/python_longitude_latitude.html
def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    # The distance returned is relative to Earth's radius. To get the distance in miles, multiply by 3960. To get the distance in kilometers, multiply by 6373.
    return arc*3960


# sum_x
def sum(x):
    ret = 0
    for i in x:
        ret = ret + i
    return ret
  
# mean_x
def mean(x):
    n = len(x)
    if n > 0:
        return sum(x)/n
    else:
        return -1

# var_x
def var(data):
    if len(data) <= 0:
        return -1
    n = 0
    mean = 0
    M2 = 0
 
    for x in data:
        n = n + 1
        delta = x - mean
        mean = mean + delta/n
        M2 = M2 + delta*(x - mean)
 
    variance = M2/(n - 1)
    return variance

# stdev_x
def stdev(x):
    if len(x) > 0:
        return math.sqrt(var(x))

# in: value, distribution
# out: 0 if non-outlier, 1 if positive outlier, 2 if negative outlier
def outlier(element, data):
    m = mean(data)
    s = stdev(data)
    if len(data) > 0:
        if (abs(element-m)/s) > 1.5: #mild outliers
            if (element-m) > 0:
                return 1,m,s
            else:
                return 2,m,s
        else:
            return 0,m,s
    return -1,m,s
        

# mysql helper
def mysql_exec(query):
    d = []
 
    #read settings, load url, parse resulting text
    settings_text = open("config.json", "r").read()
    settings = json.loads(settings_text)
    username = settings["db"]["user"] 
    password = settings["db"]["pass"] 
    database = settings["db"]["name"] 
    hostname = settings["db"]["host"] 


    try:
        con = mdb.connect(hostname, username, password, database, compress=1,cursorclass=MySQLdb.cursors.DictCursor);

        cur = con.cursor()

        cur.execute(query)
        rows = cur.fetchall()
        d=rows
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()
    return d

# in: subject, school (nullable), dataset
# out: numbers for each grade of the subject by school
def get_subject_stats_by_school(subject, school, dataset):
    query = ("SELECT SCH_SCHOOLNAME, " + subject + " AS result, count(" + subject + ") AS count FROM " + dataset + " WHERE SCH_SCHOOLNAME LIKE '%" + school + "%' GROUP BY SCH_SCHOOLNAME, " + subject)
    d = mysql_exec(query)
    return d


def get_outliers_stats_school(school, postcode, dataset):
    out = dict()
    # get student's awards
    query = ("SELECT * from " + dataset + " where `SCH_SCHOOLNAME` LIKE \"%" +school + "%\" and SCH_POSTCODE = '" + postcode + "' and KS4_PTSTNEWG <> 0 and KS5_POINTS_GA <> 0" )
    d = mysql_exec(query)
    sums_k4 = []
    sums_k5 = []

    # one row per student
    for row in d:
        this_student_k4 = row['KS4_PTSTNEWG']#0
        this_student_k5 = row['KS5_POINTS_GA']#0
        # in case you want to compute the Cambridge assessment of GCSEs/A-levels
        # adapt the following commented lines of code
        # and set the ks4grade and ks5grade at the beginning
        # more info: https://www.admin.cam.ac.uk/offices/admissions/handbook/section1/1_4.html
        #for k,v in row.iteritems():
        #    if k.startswith('KS4_AP'):
        #        if v <> "":
        #            award = ks4grade[v.strip()]
        #            this_student_k4 = this_student_k4 + award
        #    if k.startswith('KS4_AP'):
        #        if v <> "":
        #            award = ks5grade[v.strip()]
        #            this_student_k5 = this_student_k5 + award
        sums_k4.append(this_student_k4)
        sums_k5.append(this_student_k5)
    pos_k4 = 0 
    neg_k4 = 0
    m_k4 = mean(sums_k4)
    s_k4 = stdev(sums_k4)

    pos_k5 = 0 
    neg_k5 = 0
    m_k5 = mean(sums_k5)
    s_k5 = stdev(sums_k5)
 
    for student in sums_k4:     
        outl,mymean,mystdv = outlier(student,sums_k4)
        if outl == 1: #positive outlier
            pos_k4 = pos_k4 + 1
        elif outl == 2: #negative outlier
            neg_k4 = neg_k4 + 1

    for student in sums_k5:     
        outl,mymean,mystdv = outlier(student,sums_k5)
        if outl == 1: #positive outlier
            pos_k5 = pos_k5 + 1
        elif outl == 2: #negative outlier
            neg_k5 = neg_k5 + 1
          
    out['positive-outliers-k4'] = pos_k4
    out['negative-outliers-k4'] = neg_k4
    out['mean-k4'] = m_k4
    out['standard-deviation-k4'] = s_k4
    out['students-k4'] = len(sums_k4)

    out['positive-outliers-k5'] = pos_k5
    out['negative-outliers-k5'] = neg_k5
    out['mean-k5'] = m_k5
    out['standard-deviation-k5'] = s_k5
    out['students-k5'] = len(sums_k5)
    # under the assumption that we only select students who've both done GCSEs and A-Levels,
    # out['students-k4'] = out['students-k5']

    return out

# returns all schools in the given dataset
def get_all_schools(dataset):
    query = "SELECT `SCH_SCHOOLNAME`, SCH_POSTCODE from " + dataset + " GROUP BY SCH_POSTCODE"
    d = mysql_exec(query)
    return d


# returns all school within a certain radius from a given postcode
def get_schools_by_distance(postcode, distance, dataset):
    # TODO
    return



#res = get_subject_stats_by_school("KS4_APMAT", "","KS5_1011")
res = get_all_schools("KS5_1011")
for sk in res:
    postcode = sk['SCH_POSTCODE']
    print "Get " + postcode
    name = sk['SCH_SCHOOLNAME']
    res = get_outliers_stats_school(name, postcode, "KS5_1011")
    print res
#json.dumps(res, sort_keys=True, indent=4)

