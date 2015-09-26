'''
Created on 12 Sep, 2015

@author: gaia_agito
'''
import urllib
import json
import sys
import heapq
import math
from distutils.tests.test_register import RawInputs
from math import atan2
from pip._vendor.distlib.util import DIRECT_REF

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
        
    def set_notVisited(self):
        self.visited = False

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
        return(totalInfo)
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
    for v in aGraph:
            v.set_distance(sys.maxint)
            v.set_notVisited()
            v.set_previous(None)  
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
                
        # Rebuild heap
        # 1. Pop every item
        while len(unvisited_queue):
            heapq.heappop(unvisited_queue)
        # 2. Put all vertices not visited into the queue
        unvisited_queue = [(v.get_distance(),v) for v in aGraph if not v.visited]
        heapq.heapify(unvisited_queue)

# Main function
def main():
    block= raw_input("Block: ") #obtain start location
    level = raw_input("Level: ")

    
    buildingInfo=[]
    buildingInfo.append([])
    
    buildingInfo[0].append(block)
    buildingInfo[0].append(level)

    
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
            startingX = float(eachNode['x'])
            startingY = float(eachNode['y'])
            linkVertexes =eachNode['linkTo'].replace(' ','')
            linkVertexes = linkVertexes.split(",")

            for eachLink in linkVertexes:
                for nextNode in totalInfoMatrix[x]['map']:
                    if int(eachNode['nodeId']) > int(nextNode['nodeId']):
                        continue
                    if eachLink == nextNode['nodeId']:
                        endingX= float(nextNode['x']) 
                        endingY = float(nextNode['y'])

                        edgeLength = math.sqrt(math.pow((endingY - startingY),2)+ math.pow((endingX-startingX),2))
                        g.add_edge(int(eachNode['nodeId']), int(nextNode['nodeId']), edgeLength)  
                        break
                    
        mapGraph[x].append(g)
        buildingCounter = buildingCounter+1
        
    testType = int(raw_input("Test type: "))
    if testType ==1 :
        while 1:
               
            while 1:
                startNodeId = int(raw_input("Starting node: "))
                exist =False
                for everyNode in totalInfoMatrix[0]['map']:
                    
                    if int(everyNode['nodeId']) == startNodeId:
                        exist = True
                        break
                if exist == True:
                    break
                else:
                    print("Starting Node invalid.")
                    
            while 1:
                endNodeId= int(raw_input("Ending node: "))
                exist =False                
                for everyNode in totalInfoMatrix[0]['map']:
                    if int(everyNode['nodeId']) == endNodeId:
                        exist = True
                        break
                if exist == True:
                    break
                else:
                    print("Ending Node invalid.")
                    
            dijkstra(mapGraph[0][2], mapGraph[0][2].get_vertex(startNodeId), mapGraph[0][2].get_vertex(endNodeId)) 
        
            target =  mapGraph[0][2].get_vertex(endNodeId)
            path = [target.get_id()]
            shortest(target, path)
            print 'The shortest path : %s' %(path[::-1])
            
     
    elif testType ==2:             
        while 1:
            while 1:
                startNodeId = int(raw_input("Starting node: "))
                exist =False
                for everyNode in totalInfoMatrix[0]['map']:
                    if int(everyNode['nodeId']) == startNodeId:
                        exist = True
                        break
                if exist == True:
                    break
                else:
                    print("Starting Node invalid.")
                    
            while 1:
                endNodeId= int(raw_input("Ending node: "))
                exist =False
                for everyNode in totalInfoMatrix[0]['map']:
                    
                    if int(everyNode['nodeId']) == endNodeId:
                        exist = True
                        break
                if exist == True:
                    break
                else:
                    print("Ending Node invalid.")
                                       

            dijkstra(mapGraph[0][2], mapGraph[0][2].get_vertex(startNodeId), mapGraph[0][2].get_vertex(endNodeId)) 
        
            target =  mapGraph[0][2].get_vertex(endNodeId)
            path = [target.get_id()]
            shortest(target, path)            
            path = path[::-1]
            print path

            

            xCurrentLocation = float(raw_input("X coordinate: "))
            yCurrentLocation = float(raw_input("Y coordinate: "))
            currentDirection = float(raw_input("Bearings: "))

            while currentDirection>=360:
                currentDirection=currentDirection-360
            while currentDirection<=-360:
                currentDirection=currentDirection+360                
            if currentDirection<0:
                currentDirection = currentDirection + 360
            
            nextNodeCounter = 1
            for eachNode in path:
                if nextNodeCounter < len(path):
                    nextNode = path[nextNodeCounter]
                    distanceBetweenNode = mapGraph[0][2].get_vertex(eachNode).get_weight(mapGraph[0][2].get_vertex(nextNode))
                else:
                    break           
                for everyNode in totalInfoMatrix[0]['map']:
                    if int(everyNode['nodeId'])== eachNode:
                        xCurrentNode = float(everyNode['x'])
                        yCurrentNode = float(everyNode['y'])
                        distanceCurrentNode = math.sqrt(math.pow((yCurrentLocation - yCurrentNode),2)+ math.pow((xCurrentLocation-xCurrentNode),2))
                    if int(everyNode['nodeId'])== nextNode:
                        xNextNode = float(everyNode['x'])
                        yNextNode = float(everyNode['y'])
                        distanceNextNode = math.sqrt(math.pow((yCurrentLocation - yNextNode),2)+ math.pow((xCurrentLocation-xNextNode),2))
                            
                    if eachNode== path[0] and int(everyNode['nodeId']) == path[0] :
                        shortestDistance= distanceCurrentNode
                        nearestX = xCurrentNode
                        nearestY = yCurrentNode
                        nearestNode = path[0]
                                        
                if distanceNextNode <= distanceBetweenNode or distanceNextNode< shortestDistance:
                    shortestDistance= distanceNextNode
                    nearestNode = nextNode
                    nearestX = xNextNode
                    nearestY = yNextNode

                elif distanceCurrentNode < shortestDistance:
                    shortestDistance= distanceCurrentNode
                    nearestNode = eachNode
                    nearestX = xCurrentNode
                    nearestY = yCurrentNode
                nextNodeCounter = nextNodeCounter+1
            
            
            if nearestNode == path[len(path)-1] and nearestX == xCurrentLocation and nearestY == yCurrentLocation:
                print"You are at your destination."
                continue

            NorthToVert = 360 - float(totalInfoMatrix[0]['info']['northAt'])
            angleFromNorth = None
            if nearestX == xCurrentLocation and nearestY > yCurrentLocation:
                angleFromNorth = 0 + NorthToVert
            elif nearestX == xCurrentLocation and nearestY < yCurrentLocation:
                angleFromNorth = 180 + NorthToVert
            elif nearestY == yCurrentLocation and nearestX > xCurrentLocation:
                angleFromNorth = 90 + NorthToVert
            elif nearestY == yCurrentLocation and nearestX < xCurrentLocation:
                angleFromNorth = 270 + NorthToVert
            # What if on the spot itself? please CHECK
            
            if angleFromNorth == None:
                angle = atan2((nearestY-yCurrentLocation),(nearestX - xCurrentLocation))
                if angle > 90:
                    angleFromNorth = 360 - angle + 90 + NorthToVert
                else:
                    angleFromNorth = 90 - angle + NorthToVert
                    
            while angleFromNorth > 360:
                angleFromNorth = angleFromNorth -360
                
                
            directionComparison = angleFromNorth + (180 - currentDirection)
            while directionComparison> 360:
                directionComparison = directionComparison -360
            
            
            if directionComparison == 0:
                print "Travel straight ",shortestDistance,"cm to node ",nearestNode
            elif directionComparison <180:
                directionCorrection = currentDirection - angleFromNorth
                print "Turn left by ", directionCorrection," degree and travel ",shortestDistance," cm to node ",nearestNode
            else:
                directionCorrection = angleFromNorth- currentDirection
                print "Turn right by ", directionCorrection," degree and travel ",shortestDistance," cm to node ",nearestNode
    #For checking purpose 
    #To be removed on later stage
    #counter = 1

  #  for eachInfoMatrix in totalInfoMatrix:
   #     print (counter)
    #    print(eachInfoMatrix)
     #   counter = counter +1

if __name__ == "__main__":
    main()