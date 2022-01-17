# Path Finding Using A_star Algorithm

Usage:
```{bash}
python3 ./route.py [start-city] [end-city] [cost-function]
```

where:

- start-city and end-city are the cities we need a route between.
- cost-function is one of:
    + segments tries to find a route with the fewest number of road segments (i.e. edges of the graph).
    + distance tries to find a route with the shortest total distance.
    + time finds the fastest route, assuming one drives the speed limit.
    + delivery finds the fastest route, in expectation, for a certain delivery driver. Whenever this driver drives on a road with a speed limit ≥ 50 mph, there is a chance that a package will fall out of their truck and be destroyed. They will have to drive to the end of that road, turn around, return to the start city to get a replacement, then drive all the way back to where they were (they won’t make the same mistake the second time they drive on that road).
Consequently, this mistake will add an extra 2 · (troad + ttrip ) hours to their trip, where ttrip is the time it took to get from the start city to the beginning of the road, and troad is the time it takes to drive the length of the road segment.
For a road of length l miles, the probability p of this mistake happening is equal to tanh(l/1000)
if the speed limit is ≥ 50 mph, and 0 otherwise.1 This means that, in expectation, it will take troad + p · 2(troad + ttrip) hours to drive on this road.

Example:

```{bash}
python3 ./route.py Bloomington,_Indiana Indianapolis,_Indiana distance
```

### Path Finding using A* algorithm
**Search Abstraction**

**n** - Number of unique people who participated in the survey

- **State space** - A set of all roads and highways(Jct_\*) present in city-gps.txt and road-segments.txt

- **Initial state** - The start city in city-gps.txt and road-segments.txt.

- **Successor Function** - Takes the current city/highway and returns its neighbouring cities/highways with the distance, speed limit and the highway taken to reach from the current city/highway to the neighbouring city/highway.

- **Cost Function** - 
    Assuming s is the current city, s' as the successor city and z as goal, we have:

    + g(s') for segments: The number of segments traversed from starting state to s'. Everytime a successor city is explored, the cost increases by 1.
    + g(s') for distance: The distance from the start city to the city s'.
    + g(s') for time: The ratio of distance from s to s' to the speed limit from s to s', added iteratively from the start state to s'.
    + g(s') for delivery: The delivery time from state a to state b, added iteratively from the start state to s'.

    + Delivery time from the state s to s' is given by (Distance from s to s' being L):
        + Probability of mistake happening if the speed limit between s and s' is less than 50 = 0
        + Probability of mistake happening if the speed limit between s and s' is greater than or equal to 50 = p_of_mistake = tanh(L/1000)
        + Consequently, the total time = t_road + 2\*p_of_mistake\*(t_road + t_trip)
        + Here, t_road = distance/speed_limit from s to s'.
        t_trip = Delivery cost from start state to state s.

- **Heuristic Function** - Haversine distance: A straight line distance from city A to city B, accounting for the curvature of the earth. On a flat map, this path may look curved.
    + h(s',z) for segment = haversine distance divided by maximum segment length in the dataset from state s' to goal city. If the state s' is a highway, the heuristic cost is 0.
    + h(s',z) for distance = haversine distance from state s' to goal city. If the state s' is a highway, the heuristic cost is 0.
    + h(s',z) for time = haversine distance divided by maximum speed limit in the dataset from state s' to goal city. If the state s' is a highway, the heuristic cost is 0.
    + h(s',z) for delivery = haversine distance divided by maximum speed limit in the dataset from state s' to goal city. If the state s' is a highway, the heuristic cost is 0.

- **Goal state** - Goal state is the destination city/highway.

**Details**

- Is the haversine distance heuristic admissible? **Yes**, because the shortest distance between any two points on a flat surface is a straight line. In the case of a sphere(Earth), the shortest distance is the great circular distance. However, there are a few cases where haversine distance may overestimate the cost, since there are some inconsistencies in the dataset. Hence, we take a fraction of the haversine value.
- Is the heuristic for time admissible? **Yes**, since we divide the haversine distance by the maximum speed limit(65 miles), by which we always underestimate the time needed from the state s' to the goal state.
- Is the heuristic for delivery admissible? **Yes**, since we divide the haversine distance by the maximum speed limit(65 miles), by which we always underestimate the time needed from the state s' to the goal state. This heuristic is also consistent. It is due to the fact that we always underestimate a lot more than the cost function for time, given the errors in the dataset. Hence, use search algorithm 3.
- Is the heuristic for segments admissible? **Yes**, since we divide by the maximum segment length (923 miles), by which we always underestimate the number of segments needed from the state s' to the goal state. This heuristic is also consistent. It is due to the fact that the max segment length compensates for the overestimated distances due to errors in the dataset. Hence, use search algorithm 3.


**Approach**
- Dealing with cities/highways of road-segments.txt which are not in city-gps.txt (Mostly highways):
    + if start and destination nodes are highway, select the neighbouring citites from start city s' from destination highway d' such that the heuristic cost from s' to d' is minimum. Note the co-ordinates for d' for further use.
    - Else If starting node is a highway, assume the cost from start to the goal state is 0 (Uniform cost search, only at the starting node).
    - Else if destination node is a highway, select the neighbouring city from destination highway d' such that the heuristic cost from start city to d' is minimum. Note the co-ordinates for d' for further use.
    - Else compute the initial heuristic cost as heuristic cost from start city to the goal city.
- If the cost is segments or delivery, use search algorithm 3.
- Else, use search algorithm 2 with a small change. In this problem, by keeping track of the city we have already covered, we avoid going back to the previous city.

*Search Algorithm for admissible heuristic*
 ```
 If GOAL?(initial-state) then return initial-state
 INSERT(initial-node, FRINGE)
 Repeat:
    If empty(FRINGE) then return failure
    s <- REMOVE(FRINGE)
    INSERT(s, CLOSED)
    If GOAL?(s) then return s and/or path
        For every state s’ in SUCC(s):
            INSERT(s’, FRINGE)
 ```

*Search Algorithm for consistent heuristic*
 ```
 If GOAL?(initial-state) then return initial-state
 INSERT(initial-node, FRINGE)
 Repeat:
    If empty(FRINGE) then return failure
    s <- REMOVE(FRINGE)
    INSERT(s, CLOSED)
    If GOAL?(s) then return s and/or path
        For every state s’ in SUCC(s):
            If s’ in CLOSED, discard s’
            If s’ in FRINGE with larger s’, remove from FRINGE
            If s’ not in FRINGE, INSERT(s’, FRINGE)
 ```