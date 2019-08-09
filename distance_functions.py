import geopy.distance
MILE_CONV = 1.609344


def miles_to_km(miles):
    return miles * MILE_CONV


def km_to_miles(km):
    return km / MILE_CONV


def get_distance_geopy(long_1, lat_1, long_2, lat_2):
    coords_1 = (lat_1, long_1)
    coords_2 = (lat_2, long_2)
    distance = geopy.distance.distance(coords_1, coords_2).miles
    return distance


def build_zip_query(zip_code, dist):
    lat = zip_code.Latitude
    long = zip_code.Longitude
    query = "SELECT * FROM (SELECT *,(((acos(sin((" + str(lat) + "*pi()/180)) * sin((Latitude*pi()/180))" \
            "+cos((" + str(lat) + "*pi()/180)) * cos((Latitude*pi()/180)) * cos(((" + str(long) + " - Longitude)" \
            "*pi()/180))))*180/pi())*60*1.1515*1.609344) as distance FROM doctordb.postalcodes) t WHERE distance <= " + str(dist)
    return query

