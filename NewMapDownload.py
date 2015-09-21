'''
Created on 12 Sep, 2015

@author: gaia_agito
'''
import urllib
import json
import sys
import heapq
import math

class Vertex:
    def __init__(self, node):
        self.id = node
        self.adjacent = {}
        # Set distance to infinity for all nodes
        self.distance = sys.maxint
        # Mark all nodes unvisited        
        self.visited = False  
        # Predecessor
        self.previous = None

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()  

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

    def set_distance(self, dist):
        self.distance = dist

    def get_distance(self):
        return self.distance

    def set_previous(self, prev):
        self.previous = prev

    def set_visited(self):
        self.visited = True

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def get_vertices(self):
        return self.vert_dict.keys()

    def set_previous(self, current):
        self.previous = current

    def get_previous(self, current):
        return self.previous

#This function serves to download the map and load it 
#Input= Block number and Level in char
#Output= All info downloaded from the weblink
def downloadMap(mapInfo):
    try:
        mapDownload = urllib.URLopener()
        mapName = "COMXXLevelYY.json"
        url = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=COMXX&Level=YY'
        url = url.replace("XX", mapInfo[0])
        url = url.replace("YY", mapInfo[1])
        mapName = mapName.replace("XX",mapInfo[0])
        mapName = mapName.replace("YY",mapInfo[1])
        mapDownload.retrieve(url,mapName)
    
    #Load the downloaded json file into the program
        with open(mapName) as json_file:    
            totalInfo = json.load(json_file)
    except IOError:
        with open(mapName) as json_file:    
            totalInfo = json.load(json_file)
            
        return(totalInfo)

#Search for connection between this map and others
#Input= information of map
#Output= array of information ( block and level) of connecting building
def searchNewMap(mapInfo):    
    newMapInfo=[]
    for eachInfo in mapInfo:
        if "TO COM" in eachInfo['nodeName']:
            nodeName = eachInfo['nodeName']
            nodeName = nodeName.replace('TO COM','')
            newMapInfo.append(nodeName)
    return (newMapInfo)

#Check if the connection found is a new map
#Input= connected map, information of map found, total number of map currently found
#Output= information of all maps found (new and old), total number of map
def searchNewBuilding(newMapInfo,buildingInfo,totalLength):
    for eachMapInfo in newMapInfo:
        counter=0
        for eachBuildingInfo in buildingInfo:
            mapSegment = eachMapInfo.split("-")
            if mapSegment[0]== eachBuildingInfo[0] and mapSegment[1]== eachBuildingInfo[1]:
                break
            else:   
                counter = counter+1
                if totalLength == counter:
                    buildingInfo.append([])
                    buildingInfo[totalLength].append(str(mapSegment[0]))
                    buildingInfo[totalLength].append(str(mapSegment[1]))
                    totalLength = totalLength +1
    return [buildingInfo,totalLength]

def shortest(v, path):
    ''' make shortest path from v.previous'''
    if v.previous:
        path.append(v.previous.get_id())
        shortest(v.previous, path)
    return

def dijkstra(aGraph, start, target):
    print '''Dijkstra's shortest path'''
    # Set the distance for the start node to zero 
    start.set_distance(0)

    # Put tuple pair into the priority queue
    unvisited_queue = [(v.get_distance(),v) for v in aGraph]
    heapq.heapify(unvisited_queue)

    while len(unvisited_queue):
        # Pops a vertex with the smallest distance 
        uv = heapq.heappop(unvisited_queue)
        current = uv[1]
        current.set_visited()

        #for next in v.adjacent:
        for next in current.adjacent:
            # if visited, skip
            if next.visited:
                continue
            new_dist = current.get_distance() + current.get_weight(next)
            
            if new_dist < next.get_distance():
                next.set_distance(new_dist)
                next.set_previous(current)
                print 'updated : current = %s next = %s new_dist = %s' \
                        %(current.get_id(), next.get_id(), next.get_distance())
            else:
                print 'not updated : current = %s next = %s new_dist = %s' \
                        %(current.get_id(), next.get_id(), next.get_distance())

        # Rebuild heap
        # 1. Pop every item
        while len(unvisited_queue):
            heapq.heappop(unvisited_queue)
        # 2. Put all vertices not visited into the queue
        unvisited_queue = [(v.get_distance(),v) for v in aGraph if not v.visited]
        heapq.heapify(unvisited_queue)
                 
# Main function
def main():
    location = raw_input("Starting Location?") #obtain start location
    location = location.split("-")
    
    buildingInfo=[]
    buildingInfo.append([])
    buildingInfo.append([])
    
    buildingInfo[0].append(location[0])
    buildingInfo[0].append(location[1])
    buildingInfo[0].append(location[2])
    
    location = raw_input("Ending Location?") # obtain end location
    location = location.split("-")
    buildingInfo[1].append(location[0])
    buildingInfo[1].append(location[1])
    buildingInfo[1].append(location[2])
    
    totalInfoMatrix=[]
    length = 0 # Starting location for the array to download map
    totalLength = 1 # minimum number of maps
    #Loop to download all the maps that are connected directly or indirectly to starting and ending map.
    #Loop will end when no new maps are found
    #First map downloaded is the map of the ending point if it is different from the starting map
    while 1:
        if totalLength == length :
            break
        else:
            if length==1 and buildingInfo[0][0]==buildingInfo[1][0] and buildingInfo[0][1] ==buildingInfo[1][1]:
                length = length+1    
                continue
            
            totalInfo= downloadMap(buildingInfo[length])
            totalInfoMatrix.append(totalInfo)   # Stores all information of the starting map downloaded into an array
            searchLocation = len(totalInfoMatrix)-1
            newMapInfo = searchNewMap(totalInfoMatrix[searchLocation]['map'])   # extract out only the map information ( wifi and compass excluded) 
            newBuildingSearch = searchNewBuilding(newMapInfo, buildingInfo, len(buildingInfo))
 
            buildingInfo= newBuildingSearch[0]  # extract out the buildings(blocks and level) found that are linked to starting map
            totalLength = newBuildingSearch[1]  # extract out the total number of buildings found    
            length = length+1


         
    if buildingInfo[0][0]==buildingInfo[1][0] and buildingInfo[0][1] ==buildingInfo[1][1]:
        maxRange = len(buildingInfo)-1
    else:
        maxRange = len(buildingInfo)   
            

    mapGraph=[]
    buildingCounter = 0
    for x in xrange(0, maxRange):
        mapGraph.append([])
        g = Graph()
        if buildingInfo[x][0]== buildingInfo[x-1][0] and buildingInfo[x][1]== buildingInfo[x-1][1]:
            buildingCounter = buildingCounter+1
        mapGraph[x].append(buildingInfo[buildingCounter][0])
        mapGraph[x].append(buildingInfo[buildingCounter][1])
        
        for eachNode in totalInfoMatrix[x]['map']:
            g.add_vertex(int(eachNode['nodeId']))

        for eachNode in totalInfoMatrix[x]['map']:
            startingX = int(eachNode['x'])
            startingY = int(eachNode['y'])
            linkVertexes =eachNode['linkTo'].replace(' ','')
            linkVertexes = linkVertexes.split(",")

            for eachLink in linkVertexes:
                for nextNode in totalInfoMatrix[x]['map']:
                    if int(eachNode['nodeId']) > int(nextNode['nodeId']):
                        continue
                    if eachLink == nextNode['nodeId']:
                        endingX= int(nextNode['x'])
                        endingY = int(nextNode['y'])

                        edgeLength = math.sqrt(math.pow((endingY - startingY),2)+ math.pow((endingX-startingX),2))
                        g.add_edge(int(eachNode['nodeId']), int(nextNode['nodeId']), edgeLength)  
                        break
                    
        mapGraph[x].append(g)
        buildingCounter = buildingCounter+1

    for x in mapGraph:
        print x
        
    print 'Graph data:'
    for v in mapGraph[0][2]:
        print v
        for w in v.get_connections():
            vid = v.get_id()
            wid = w.get_id()
            print '( %s , %s, %3d)'  % ( vid, wid, v.get_weight(w))

    dijkstra(mapGraph[0][2], mapGraph[0][2].get_vertex(int(buildingInfo[0][2])), mapGraph[0][2].get_vertex(int(buildingInfo[1][2]))) 

    target = mapGraph[0][2].get_vertex(int(buildingInfo[1][2]))
    path = [target.get_id()]
    shortest(target, path)
    print 'The shortest path : %s' %(path[::-1])
    #For checking purpose 
    #To be removed on later stage
    #counter = 1

  #  for eachInfoMatrix in totalInfoMatrix:
   #     print (counter)
    #    print(eachInfoMatrix)
     #   counter = counter +1

if __name__ == "__main__":
    main()