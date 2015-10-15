'''
Created on 12 Sep, 2015

@author: gaia_agito
'''
import urllib
import json
import sys
import heapq
import math
#from distutils.tests.test_register import RawInput
from math import atan2
#from pip._vendor.distlib.util import DIRECT_REF
from AudioManager import AudioManager

audioManager = AudioManager()

class Vertex:
    def __init__(self, node, name,x,y):
        self.name=name
        self.id = node
        self.adjacent = {}
        # Set distance to infinity for all nodes
        self.distance = sys.maxint
        # Mark all nodes unvisited        
        self.visited = False  
        # Predecessor
        self.previous = None
        self.x=x
        self.y=y

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()  

    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

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
    def __init__(self,block,level,north):
        self.block = block
        self.level = level
        self.vert_dict = {}
        self.num_vertices = 0
        self.north = 0

    def __iter__(self):
        return iter(self.vert_dict.values())
    

    def get_block(self):
        return self.block
    
    def get_level(self):
        return self.level
            
    def get_north(self):
        return self.north

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
        mapName = "XXLevelYY.json"
        
        url = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=XX&Level=YY'
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
        if "TO" in eachInfo['nodeName']:
            nodeName = eachInfo['nodeName']
            nodeName = nodeName.replace('TO ','')
            newMapInfo.append(nodeName)
    return (newMapInfo)

#Check if the connection found is a new map
#Input= connected map, information of map found, total number of map currently found
#Output= information of all maps found (new and old), total number of map
def searchNewBuilding(newMapInfo,buildingInfo,totalLength):
    for eachMapInfo in newMapInfo:
        counter=0
        for eachBuildingInfo in buildingInfo:

            if "-" in str(eachMapInfo):
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
            else:
                if eachMapInfo == eachBuildingInfo[0]:
                    break
                else:
                    counter = counter+1
                    if totalLength == counter:
                        buildingInfo.append([])
                        buildingInfo[totalLength].append(str(eachMapInfo))
                        buildingInfo[totalLength].append("1")
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

def startup():
    while 1: 
        while 1:
            audioManager.playRequestStartingBlock()
            startBlock= raw_input() #obtain start location
            audioManager.playRequestStartingLevel()
            startLevel = raw_input()
            if '*' in startBlock or '*' in startLevel:
                audioManager.playStartingBlockLevelInvalid()
            else:
                break
            
        buildingInfo=[]
        buildingInfo.append([])

    
        buildingInfo[0].append(startBlock)
        buildingInfo[0].append(startLevel)
        buildingInfo[0].append("Start")
        totalInfo= downloadMap(buildingInfo[0])
        if totalInfo['info'] != None:
            break
        else:
            audioManager.playStartingBlockLevelInvalid()
            #print("Block/ Level is invalid")
            

    #Download all map linked to this building
    totalInfoMatrix=[]
    totalInfoMatrix.append(totalInfo)   # Stores all information of the starting map downloaded into an array
    
    while 1:#Loop to check if the node exist
        while 1:#Loop to check for valid input
            try:
                audioManager.playRequestStartingNode()
                startNode = int(raw_input())
            except ValueError:
                audioManager.playStartingNodeIntegerError()
                #print("Input invalid")
            else:
                break

        exist =False
        for everyNode in totalInfoMatrix[0]['map']:
            
            if int(everyNode['nodeId']) == startNode:
                exist = True
                break
        if exist == True:
            break
        else:
            audioManager.playStartingNodeInvalid()
            #print("Starting Node invalid.")        
    
    searchLocation = len(totalInfoMatrix)-1
    newMapInfo = searchNewMap(totalInfoMatrix[searchLocation]['map'])   # search through the map and see if it links to a new map
    if len(newMapInfo)!=0:
        newBuildingSearch = searchNewBuilding(newMapInfo, buildingInfo, len(buildingInfo))
        buildingInfo= newBuildingSearch[0]  # extract out the buildings(blocks and level) found that are linked to starting map
        totalLength = newBuildingSearch[1]  # extract out the total number of buildings found       

        length = 1 # Starting location for the array to download map
        #Loop to download all the maps that are connected directly or indirectly to starting and ending map.
        #Loop will end when no new maps are found
        #First map downloaded is the map of the ending point if it is different from the starting map
        while 1:
            if totalLength == length :
                break
            else:
                
                totalInfo= downloadMap(buildingInfo[length])
                if totalInfo['info'] != None:
                    totalInfoMatrix.append(totalInfo)   # Stores all information of the starting map downloaded into an array
                    searchLocation = len(totalInfoMatrix)-1
                    newMapInfo = searchNewMap(totalInfoMatrix[searchLocation]['map'])   # extract out only the map information ( wifi and compass excluded) 
                    newBuildingSearch = searchNewBuilding(newMapInfo, buildingInfo, len(buildingInfo))
     
                    buildingInfo= newBuildingSearch[0]  # extract out the buildings(blocks and level) found that are linked to starting map
                    totalLength = newBuildingSearch[1]  # extract out the total number of buildings found    
                    length = length+1
                    
                else:
                    buildingInfo.pop(length)
                    totalLength = totalLength - 1
                
    while 1:
        audioManager.playRequestEndingBlock()
        endBlock= raw_input() #obtain start location
        audioManager.playRequestEndingLevel()
        endLevel = raw_input()

        
        counter =0
        for eachMap in buildingInfo:
            counter +=1
            if eachMap[0] == endBlock and eachMap[1] == endLevel:
                counter -=1
                if len(eachMap) == 3 and eachMap[2]== "Start":
                    eachMap[2]="Same"
                    break 
                if len(eachMap)==2:
                    eachMap.append("End")
                    break
        
        if len(buildingInfo)== counter:
            audioManager.playEndingBlockLevelInvalid()
            #print("Invalid end block/level")
        else:
            break

    while 1:#Loop to check if the node exist
        while 1:#Loop to check for valid input
            try:
                audioManager.playRequestEndingNode()
                endNode = int(raw_input())
            except ValueError:
                audioManager.playEndingNodeIntegerError()
                #print("Input invalid")
            else:
                break

        exist =False
        counter = 0
        for everyMap in buildingInfo:
            if everyMap[-1]=="End" or everyMap[-1]=="Same":
                break
            counter += 1            
        for everyNode in totalInfoMatrix[counter]['map']:
            
            if int(everyNode['nodeId']) == endNode:
                exist = True
                break
        if exist == True:
            break
        else:
            audioManager.playEndingNodeInvalid()
            #print("Ending Node invalid.")
    return (startNode, endNode,buildingInfo,totalInfoMatrix)     

def parseInfo(buildingInfo,totalInfoMatrix):
    maxRange = len(buildingInfo)
    
    mapGraph=[]

    #Assigning edge connected to each node
    for x in xrange(0, maxRange):
        mapGraph.append([])
        g = Graph(buildingInfo[x][0],buildingInfo[x][1],int(totalInfoMatrix[x]['info']['northAt']))
        
        
        for eachNode in totalInfoMatrix[x]['map']:
            g.add_vertex(int(eachNode['nodeId']), str(eachNode['nodeName']), int(eachNode['x']), int(eachNode['y']))

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
        if len(buildingInfo[x]) >2:
            mapGraph[x].append(buildingInfo[x][-1])
    
    return mapGraph

def shortestPath(mapGraph,startNode,endNode):
    for eachGraph in mapGraph:
        if eachGraph[-1]== "Same":
            dijkstra(eachGraph[-2], eachGraph[-2].get_vertex(startNode), eachGraph[-2].get_vertex(endNode))
            target =  eachGraph[-2].get_vertex(endNode)
            path = [target.get_id()]
            shortest(target, path)            
            path = path[::-1]
    return path
                
def travelDirection(currentDirection, currentX, currentY, path, mapGraph):
    for eachGraph in mapGraph:
        if eachGraph[-1]== "Same":  
            nextX =eachGraph[-2].get_vertex(int(path[0])).get_x()
            nextY = eachGraph[-2].get_vertex(int(path[0])).get_y()
             
            distance = math.sqrt(math.pow((currentX-nextX),2)+ math.pow((currentY-nextY),2))
            if distance <30:
                # reset x and y
                path.pop(0)
                if len(path)==0:
                    print "You have reached your destination"
                    break
                nextX =eachGraph[-2].get_vertex(int(path[0])).get_x()
                nextY = eachGraph[-2].get_vertex(int(path[0])).get_y()
                distance = math.sqrt(math.pow((currentX-nextX),2)+ math.pow((currentY-nextY),2))
            
            NorthToVert = 360 - eachGraph[-2].get_north()
            #Find angle to travel with respect to north from current location to next node
            angleToTravel = None
            if nextX == currentX and nextY > currentY:
                angleToTravel = 0 + NorthToVert
            elif nextX == currentX and nextY < currentY:
                angleToTravel = 180 + NorthToVert
            elif nextY == currentY and nextX > currentX:
                angleToTravel = 90 + NorthToVert
            elif nextY == currentY and nextX < currentX:
                angleToTravel = 270 + NorthToVert
                
            if angleToTravel == None:
                angle = math.degrees(atan2((nextY-currentY),(nextX - currentX)))
            if angle > 90:
                angleToTravel = 360 - angle + 90 + NorthToVert
            else:
                angleToTravel = 90 - angle + NorthToVert
                    
            while angleToTravel >= 360:
                angleToTravel = angleToTravel -360
            
            angleRangeMax = angleToTravel + 45
            angleRangeMin = angleToTravel - 45
            while angleRangeMax >= 360:
                angleRangeMax -= 360
            
            while angleRangeMin<0:
                angleRangeMin+=360
            
            leftDirection = currentDirection -180
            if leftDirection<0:
                leftDirection= leftDirection+360
            
            if (angleRangeMin<= currentDirection and currentDirection<360) or (angleRangeMax>= currentDirection and currentDirection>=0) or (angleRangeMin<= currentDirection and currentDirection<=angleRangeMax):
                print "Travel straight %.2f"%distance,"cm to node",path[0]
            elif (angleToTravel <currentDirection and angleToTravel > leftDirection and leftDirection <180) or (((angleToTravel<currentDirection) or (angleToTravel > leftDirection)) and leftDirection >=180):
                directionCorrection = currentDirection - angleToTravel
                while directionCorrection<0:
                    directionCorrection = directionCorrection+360
                print "Turn left by %.2f" %directionCorrection,"degree and travel %.2f" %distance,"cm to node",path[0]
            else:
                directionCorrection = angleToTravel- currentDirection
                while directionCorrection<0:
                    directionCorrection = directionCorrection+360
                print "Turn right by %.2f" %directionCorrection,"degree and travel %.2f" %distance,"cm to node",path[0]
            break
    return path    
                
