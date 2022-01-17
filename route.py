#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: Srimanth Agastyaraju, sragas
#
# Based on skeleton code by V. Mathur and D. Crandall, January 2021
#


# !/usr/bin/env python3
import sys
from math import cos, asin, sqrt, pi, tanh

import heapq



def read_city_gps_data(path):
    """ Reads the city-gps.txt from the file path.
    Returns a dictionary containing cities as keys and a tuple of latitudes and longitudes as values.

    Args:
        path (str): A string containing the relative path of city-gps.txt

    Returns:
        [dict]: A dictionary containing cities as keys and a tuple of latitudes and longitudes as values.
    """
    city_gps_data = {}
    with open(path,'r') as data:
        for line in data:
            city, latitude, longitude = line.split(' ')
            longitude = longitude.replace('\n','')
            
            # new_line.append()
            city_gps_data[city] = (float(latitude), float(longitude))
    return city_gps_data



def read_road_data(path):
    """ Reads the road-segments.txt from the file path.
    Returns a list of tuples, each tuple containing city 1; city 2; distance, speed limit and highway taken from city 1 to 2

    Args:
        path (str): A string containing the relative path of road-segments.txt

    Returns:
        [list(tuple)]: Returns a list of tuples, each tuple containing city 1; city 2; distance, speed limit and highway taken from city 1 to 2
    """
    road_data = []
    with open(path,'r') as data:
        for line in data:
            city_1, city_2, distance, speed_limit, highway = line.split(' ')
            highway = highway.replace('\n','')
            new_line = (city_1, city_2, distance, speed_limit, highway)
            # new_line.append()
            road_data.append(new_line)
    return road_data


def get_max_values_in_roads(road_data):
    """Gives the maximum speed limit and maximum segment length, given the processed road-segments.txt data (list of tuples).

    Args:
        road_data (list(tuples)): A formatted list of tuples of road-segments.txt

    Returns:
        [tuple]: tuple of maximum speed limit and maximum segment length
    """
    max_speed_limit = -9999
    max_segment_length = -9999
    for _, _, distance, speed_limit, _ in road_data:
        if(max_speed_limit < int(speed_limit)):
            max_speed_limit = int(speed_limit)
        if(max_segment_length < int(distance)):
            max_segment_length = int(distance)
    
    return max_speed_limit, max_segment_length


def successors(start_city, road_data):
    """ Takes the start city and returns all possible neighbours of the start_city.

    Args:
        start_city (str): A city or highway in the following format: 'city/hwy,_State'
        road_data (list(tuples)): A formatted list of tuples of road-segments.txt

    Returns:
        [list]: A list of all possible neighbours of the start_city.
    """
    dest_successors = []
    for city_1, city_2, distance, speed_limit, highway in road_data:
        dest_city = ''
        if(start_city == city_1):
            dest_city = city_2
        elif(start_city == city_2):
            dest_city = city_1
        if(dest_city != ''):
            dest_successors.append([dest_city, int(distance), int(speed_limit), highway])
    return dest_successors



def is_goal(city, dest_city):
    """Checks if we have reached the goal or not.

    Args:
        city (str): A city or highway in the following format: 'city/hwy,_State'
        dest_city (str): A city or highway in the following format: 'city/hwy,_State'

    Returns:
        [bool]: returns True if city is equal to destination city. Otherwise returns False.
    """
    return city == dest_city



def haversine(theta):
    """Haversine value of an angle.
    https://en.wikipedia.org/wiki/Haversine_formula

    Args:
        theta (float): A value of angle in radians.

    Returns:
        [float]: The haversine value of the angle.
    """
    return (1 - cos(theta)) / 2


def heuristic_haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2):
    """Calculates the haversine distance between two cities, given their latitudes and longitudes.
    https://en.wikipedia.org/wiki/Haversine_formula

    Args:
        latitude_1 (float): Latitude value of first city
        longitude_1 (float): Longitude value of first city
        latitude_2 (float): Latitude value of second city
        longitude_2 (float): Longitude value of second city

    Returns:
        [float]: Haversine distance between first and second city in miles.
    """
    pi_by_180 = pi/180
    phi_1 = latitude_1 * pi_by_180
    phi_2 = latitude_2 * pi_by_180
    lambda_1 = longitude_1 * pi_by_180
    lambda_2 = longitude_2 * pi_by_180
    
    h = sqrt(haversine(phi_2-phi_1) + (cos(phi_2) * cos(phi_1) * haversine(lambda_2 - lambda_1)))

    return 7917.6 * asin(h) # 2 * radius_of_earth_in_miles = 2 * 3,958.8 = 7917.6



def find_in_cities(key_city, city_gps_data):
    """Looks up a city in the processed city-gps.txt (dict).
    Returns co-ordinates if found. Otherwise, returns -1.

    Args:
        key_city (str): A city or highway in the following format: 'city/hwy,_State'
        city_gps_data (dict): Processed city-gps.txt (dict).

    Returns:
        [tuple]: Returns latitude and longitude of the corresponding city if found
        or
        [int]: Returns -1 if not found
    """

    try:
        return city_gps_data[key_city]
    except KeyError as ke:
        return -1



def euclidean_distance(latitude_1, longitude_1, latitude_2, longitude_2):
    # distance b/w 2 latitudes = 69 miles
    # https://www.usgs.gov/faqs/how-much-distance-does-a-degree-minute-and-second-cover-your-maps?qt-news_science_products=0#qt-news_science_products

    x = (latitude_2  - latitude_1) * 69
    y = (longitude_2 - longitude_1) * 52

    heuristic_value = sqrt((x ** 2) + (y ** 2))
    return heuristic_value 


def chebyshev(latitude_1, longitude_1, latitude_2,  longitude_2):
    # distance b/w 2 latitudes = 69 miles
    # https://www.usgs.gov/faqs/how-much-distance-does-a-degree-minute-and-second-cover-your-maps?qt-news_science_products=0#qt-news_science_products

    x = (latitude_2  - latitude_1) * 69
    y = (longitude_2 - longitude_1) * 52

    heuristic_value = max(x,y)
    return heuristic_value




def heuristic(latitude_1, longitude_1, latitude_2, longitude_2, cost, max_speed_limit, max_segment_length):
    """Returns a heuristic value depending on the cost.
    h(s',z) for distance = fraction of haversine distance from state s' to goal city
    h(s',z) for segment = haversine distance divided by maximum segment length
    h(s',z) for time = haversine distance divided by maximum speed limit
    h(s',z) for delivery = haversine distance divided by maximum speed limit

    Args:
        latitude_1 (float): Latitude value of first city
        longitude_1 (float): Longitude value of first city
        latitude_2 (float): Latitude value of second city
        longitude_1 (float): Longitude value of second city
        cost (str): A string which mentions the cost category.
        max_speed_limit (float): maximum speed limit, given the processed road-segments.txt data (list of tuples)
        max_segment_length (float): maximum segment length, given the processed road-segments.txt data (list of tuples)

    Returns:
        float: Heuristic cost from city 1 to city 2, given the cost.
    """
    if(cost == 'distance'):
        return heuristic_haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2) - 20
    elif(cost == 'time'):
        return heuristic_haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2) / max_speed_limit
    elif(cost == 'segments'):
        return heuristic_haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2) / max_segment_length
    elif(cost == 'delivery'):
        return heuristic_haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2) / max_speed_limit




def A_star(start_city, dest_city, cost):
    """A_Star algorithm applied to get the path from start city to destination city, given the cost.

    Args:
        start_city (str): The city/highway to in the map to start.
        dest_city (str): The city/highway to in the map to reach.
        cost (str): A string which mentions the cost category.

    Returns:
        [tuple]: Returns the distance, time, delivery time and path taken, if the city is found.
        [str]: Returns start city otherwise.
    """

    city_gps_data = read_city_gps_data('./city-gps.txt')
    road_data = read_road_data('./road-segments.txt')

    max_speed_limit, max_segment_length = get_max_values_in_roads(road_data)

    if(find_in_cities(start_city, city_gps_data) != -1 and find_in_cities(dest_city, city_gps_data) != -1):
        start_latitude, start_longitude = find_in_cities(start_city, city_gps_data)
        destination_latitude, destination_longitude = find_in_cities(dest_city, city_gps_data)
        initial_h_of_x = heuristic(start_latitude, start_longitude, destination_latitude, destination_longitude, cost, max_speed_limit, max_segment_length)
    elif(find_in_cities(start_city, city_gps_data) == -1 and find_in_cities(dest_city, city_gps_data) != -1):
        initial_h_of_x = 0
        destination_latitude, destination_longitude = find_in_cities(dest_city, city_gps_data)
    elif(find_in_cities(dest_city, city_gps_data) == -1 and find_in_cities(start_city, city_gps_data) != -1):
        min_heuristic_val = 9999
        for new_city, new_dist, new_speed_limit, new_highway in successors( dest_city, road_data ):
            if(find_in_cities(new_city, city_gps_data) != -1):
                alt_lat, alt_long = find_in_cities(new_city, city_gps_data)
                if(find_in_cities(start_city, city_gps_data) != -1):
                    start_lat, start_long = find_in_cities(start_city, city_gps_data)
                    if(min_heuristic_val > heuristic(start_lat, start_long, alt_lat, alt_long, cost, max_speed_limit, max_segment_length)):
                        min_heuristic_val = heuristic(start_lat, start_long, alt_lat, alt_long, cost, max_speed_limit, max_segment_length)
                        destination_latitude, destination_longitude = alt_lat, alt_long
        initial_h_of_x = min_heuristic_val
    else:
        alt_start_cities = []
        alt_dest_cities = []
        for new_city, new_dist, new_speed_limit, new_highway in successors( start_city, road_data ):
            if(find_in_cities(new_city, city_gps_data) != -1):
                alt_start_cities.append(new_city)
        for new_city, new_dist, new_speed_limit, new_highway in successors( dest_city, road_data ):
            if(find_in_cities(new_city, city_gps_data) != -1):
                alt_dest_cities.append(new_city)
        
        min_heuristic_val = 9999
        for alt_start_city in alt_start_cities:
            for alt_dest_city in alt_dest_cities:
                alt_start_lat, alt_start_long = find_in_cities(alt_start_city, city_gps_data)
                alt_dest_lat, alt_dest_long = find_in_cities(alt_dest_city, city_gps_data)
                if(min_heuristic_val > heuristic(alt_start_lat, alt_start_long, alt_dest_lat, alt_dest_long, cost, max_speed_limit, max_segment_length)):
                    min_heuristic_val = heuristic(alt_start_lat, alt_start_long, alt_dest_lat, alt_dest_long, cost, max_speed_limit, max_segment_length)
                    start_latitude, start_longitude = alt_start_lat, alt_start_long
                    destination_latitude, destination_longitude = alt_dest_lat, alt_dest_long
        initial_h_of_x = min_heuristic_val

    fringe = []
    heapq.heappush(fringe, (initial_h_of_x, start_city, 0, 1, '', 0, 0, []))

    visited_cities = []
    g_of_x = 0
    p_of_mistake = 0
    t_road = 0
    next_delivery_time = 0

    if is_goal(start_city, dest_city):
        return((0, 0, 0, [(start_city, '' + ' for ' + str(0) + ' miles')]))

    while len(fringe)>0:
        g_plus_h, current_city, current_dist, current_speed_limit, current_highway, current_time, current_delivery_time, path_so_far = heapq.heappop(fringe)
        visited_cities.append(current_city)
        
        
        if is_goal(current_city, dest_city):
            return (current_dist, current_time, current_delivery_time, path_so_far)



        for new_city, new_dist, new_speed_limit, new_highway in successors( current_city, road_data ):
            if(new_city not in visited_cities):

                p_of_mistake = 0
                if(new_speed_limit >= 50):
                    p_of_mistake = tanh(new_dist/1000)
                
                t_road = new_dist / new_speed_limit
                t_trip = current_delivery_time
                next_delivery_time = t_road + (2 * p_of_mistake * (t_road + t_trip))

                if(cost == 'distance'):
                    g_of_x = current_dist + new_dist
                elif(cost == 'time'):
                    g_of_x = current_time + int(new_dist)/int(new_speed_limit)
                elif(cost == 'segments'):
                    g_of_x = len(path_so_far) + 1
                elif(cost == 'delivery'):
                    g_of_x = current_delivery_time + next_delivery_time


                if find_in_cities(new_city, city_gps_data)== -1:
                    h_of_x = 0
                else:
                    latitude_1, longitude_1 = find_in_cities(new_city, city_gps_data)
                    h_of_x = heuristic(latitude_1, longitude_1, destination_latitude, destination_longitude, cost, max_speed_limit, max_segment_length)


                
                if(cost == 'segments' or cost == 'delivery'):
                    # Turns out, the heuristic for segments and delivery is consistent. Hence, use search algorithm #3
                    # Code for same_city_index_in_fringe and same_city_index_in_visited is modeled after the following link:
                    # https://stackoverflow.com/questions/2917372/how-to-search-a-list-of-tuples-in-python
                    same_city_index_in_fringe = next((i for i, fringe_item in enumerate(fringe) if fringe_item[1] == new_city), None)
                    same_city_index_in_visited = next((i for i, city in enumerate(visited_cities) if city == new_city), None)
                    if(same_city_index_in_visited is not None):
                        visited_cities.pop(same_city_index_in_visited)
                    if(same_city_index_in_fringe is not None):
                        if(g_of_x + h_of_x < fringe[same_city_index_in_fringe][0]):
                            fringe.pop(same_city_index_in_fringe)
                            new_fringe_item = (g_of_x + h_of_x, new_city, 
                                            current_dist + int(new_dist), 
                                            new_speed_limit, new_highway, 
                                            current_time + int(new_dist)/int(new_speed_limit),
                                            current_delivery_time + next_delivery_time,
                                            path_so_far + [(new_city, new_highway + ' for ' + str(new_dist) + ' miles')])
                        
                            heapq.heappush(fringe, new_fringe_item)
                    else:
                        new_fringe_item = (g_of_x + h_of_x, new_city, 
                                            current_dist + int(new_dist), 
                                            new_speed_limit, new_highway, 
                                            current_time + int(new_dist)/int(new_speed_limit),
                                            current_delivery_time + next_delivery_time,
                                            path_so_far + [(new_city, new_highway + ' for ' + str(new_dist) + ' miles')])
                        
                        heapq.heappush(fringe, new_fringe_item)
                else:
                    new_fringe_item = (g_of_x + h_of_x, new_city, 
                                            current_dist + int(new_dist), 
                                            new_speed_limit, new_highway, 
                                            current_time + int(new_dist)/int(new_speed_limit),
                                            current_delivery_time + next_delivery_time,
                                            path_so_far + [(new_city, new_highway + ' for ' + str(new_dist) + ' miles')])
                        
                    heapq.heappush(fringe, new_fringe_item)

    return start_city



def get_route(start, end, cost):
    
    """
    Find shortest driving route between start city and end city
    based on a cost function.

    1. Your function should return a dictionary having the following keys:
        -"route-taken" : a list of pairs of the form (next-stop, segment-info), where
           next-stop is a string giving the next stop in the route, and segment-info is a free-form
           string containing information about the segment that will be displayed to the user.
           (segment-info is not inspected by the automatic testing program).
        -"total-segments": an integer indicating number of segments in the route-taken
        -"total-miles": a float indicating total number of miles in the route-taken
        -"total-hours": a float indicating total amount of time in the route-taken
        -"total-delivery-hours": a float indicating the expected (average) time 
                                   it will take a delivery driver who may need to return to get a new package
    2. Do not add any extra parameters to the get_route() function, or it will break our grading and testing code.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """
    

    final_distance, final_time, final_delivery_time, final_path = A_star(start, end, cost)

    # print("{} {} {} {} {}".format(final_path, len(final_path), float(final_distance), float(final_time), float(final_delivery_time)))
    
    
    return {"total-segments" : len(final_path), 
            "total-miles" : float(final_distance), 
            "total-hours" : float(final_time), 
            "total-delivery-hours" : float(final_delivery_time), 
            "route-taken" : final_path}


# Please don't modify anything below this line
#
if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise(Exception("Error: expected 3 arguments"))

    (_, start_city, end_city, cost_function) = sys.argv
    if cost_function not in ("segments", "distance", "time", "delivery"):
        raise(Exception("Error: invalid cost function"))

    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    for step in result["route-taken"]:
        print("   Then go to %s via %s" % step)

    print("\n          Total segments: %4d" % result["total-segments"])
    print("             Total miles: %8.3f" % result["total-miles"])
    print("             Total hours: %8.3f" % result["total-hours"])
    print("Total hours for delivery: %8.3f" % result["total-delivery-hours"])


