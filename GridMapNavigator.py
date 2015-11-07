'''
Created on Oct 23, 2015

@author: bamboo3250
'''
import urllib
import json
import math 
import AudioManager
import os
import heapq
from MapManager import MapManager

class GridMapNavigator(object):
    mapManager = MapManager()
    map = []
    obstacleMap = []
    minDist = []
    mapHeading = 0
    startNode = {}
    endNode = {}
    curBuilding = 1
    curLevel = 2
    source = ()
    destination = ()
    curX = 0 
    curY = 0
    curHeading = 0
    pathToGo = []
    hasReachedDestination = False
    
    ANGLE_LIMIT = 20
    INF = 1000000000
    STEP_LENGTH = 42
    GRID_LENGTH = 50
    maxXGrid = 0
    maxYGrid = 0
    
    hasUpdate = False
    nextDir = [[0,1,0],[1,1,45],[1,0,90],[1,-1,135],[0,-1, 180],[-1,-1, 225],[-1, 0, 270],[-1,1, 315]]
    
    def getCurrentPos(self):
        return [self.curX, self.curY, self.curHeading]
    
    def isInsideMapGrid(self, x, y):
        return (0 <= x) and (x < self.maxXGrid) and (0 <= y) and (y < self.maxYGrid)
    
    def isValidPoint(self, x, y):
        return self.isInsideMapGrid(x, y) and (self.map[x][y] != 0) and (self.obstacleMap[x][y] == False)
    
    def stepAhead(self, numSteps):
        totalHeading = 90 - (self.curHeading + self.mapHeading)
        nextX = self.curX + numSteps * self.STEP_LENGTH * math.cos(math.radians(totalHeading))
        nextY = self.curY + numSteps * self.STEP_LENGTH * math.sin(math.radians(totalHeading))
        if self.isValidPoint(int(nextX / self.GRID_LENGTH), int(nextY / self.GRID_LENGTH)):
            self.curX = nextX
            self.curY = nextY
        elif self.isValidPoint(int(nextX / self.GRID_LENGTH), int(self.curY / self.GRID_LENGTH)):
            self.curX = nextX
        elif self.isValidPoint(int(self.curX / self.GRID_LENGTH), int(nextY / self.GRID_LENGTH)):
            self.curY = nextY
    
    def create2DArray(self, n, m, initValue):
        return [[initValue for i in range(n)] for j in range(m)]
    
    def __init__(self):
        self.maxXGrid = 200*100/self.GRID_LENGTH
        self.maxYGrid = 200*100/self.GRID_LENGTH
        self.map = self.create2DArray(self.maxXGrid, self.maxYGrid, 0)
        print "finish creating map"
        self.minDist = self.create2DArray(self.maxXGrid, self.maxYGrid, 0)
        print "finish creating minDist"
        self.obstacleMap = self.create2DArray(self.maxXGrid, self.maxYGrid, True)
        print "finish creating obstacleMap"
    
    def dist(self, u, v):
        return math.sqrt(math.pow(v['x'] - u['x'],2) + math.pow(v['y'] - u['y'],2))
    
    def mark(self, u, value):
        for i in range(-2,3):
            for j in range(-2,3):
                x = int(u['x']/self.GRID_LENGTH) + i
                y = int(u['y']/self.GRID_LENGTH) + j
                if self.isInsideMapGrid(x, y):
                    self.map[x][y] = value
                    if (value != 0) :
                        self.obstacleMap[x][y] = False
    
    def drawRoute(self, s, t, value):
        length = self.dist(s,t)
        direction = [(t['x'] - s['x']) / length*self.GRID_LENGTH, (t['y'] - s['y']) / length*self.GRID_LENGTH]    # 1 meter
        u = dict(s)
        count = 0
        while self.dist(u, t) >= self.GRID_LENGTH:
            #print str(u['x']) + " " + str(u['y']) + " " + str(count)
            self.mark(u, value)
            count = count + 1
            u['x'] = int(s['x'] + direction[0] * count)
            u['y'] = int(s['y'] + direction[1] * count)
            #print str(u['x']) + "->" + str(s['x']) + " " + str(count) + " " + str(direction[0] * count)
    
    def clearMinDist(self):
        print "Clearing minDist"
        count = 0
        if len(self.pathToGo) > 1:
            curNode = self.mapManager.getNode(self.pathToGo[0][0], self.pathToGo[0][1], self.pathToGo[0][2])
            nextNode = self.mapManager.getNode(self.pathToGo[1][0], self.pathToGo[1][1], self.pathToGo[1][2])
            minX = int(min(curNode.x, nextNode.x) / self.GRID_LENGTH) - 2
            maxX = int(max(curNode.x, nextNode.x) / self.GRID_LENGTH) + 2
            minY = int(min(curNode.y, nextNode.y) / self.GRID_LENGTH) - 2
            maxY = int(max(curNode.y, nextNode.y) / self.GRID_LENGTH) + 2
            for i in range(minX, maxX + 1):
                for j in range(minY, maxY + 1):
                    if self.isInsideMapGrid(i, j):
                        self.minDist[i][j] = self.INF
                        count = count + 1
        print "Finished clearing minDist", count, "cells"
    
    def dijkstra(self, startNode, endNode):
        #print "dijkstra from",startNode.code," to", endNode.code
        d = {}
        parent = {}
        
        d[startNode.code] = 0
        parent[startNode.code] = None
        priority_queue = [(d[startNode.code], startNode)]
        heapq.heapify(priority_queue)
    
        while len(priority_queue) > 0:
            pair = heapq.heappop(priority_queue)
            u = pair[1]
            if pair[0] != d[u.code]:
                continue
            if u == endNode:
                break
            
            for i in range(0, len(u.linkTo)):
                v = self.mapManager.getNode(u.block, u.level, u.linkTo[i])
                w = self.dist(u.getPos(), v.getPos())
                if self.mapManager.canPass(u.block, u.level, u.nodeId, v.nodeId) and ((d.has_key(v.code) == False) or (d[v.code] > d[u.code] + w)):
                    parent[v.code] = u
                    #print u.code,"=>",v.code
                    d[v.code] = d[u.code] + w
                    heapq.heappush(priority_queue, (d[v.code],v))
            
            if u.specialLinkTo != None:
                #print v.code,u.specialLinkTo
                v = self.mapManager.getNode(u.specialLinkTo[0], u.specialLinkTo[1], u.specialLinkTo[2])
                if (v != None) and ((d.has_key(v.code) == False) or (d[v.code] > d[u.code])):
                    parent[v.code] = u
                    d[v.code] = d[u.code]
                    #print u.code,"===>",v.code
                    heapq.heappush(priority_queue, (d[v.code],v))
                
        result = []
        temp = endNode
        while temp != None:
            result.append((temp.block, temp.level, temp.nodeId))
            temp = parent[temp.code]
            
        for i in range(0, len(result)/2):
            temp = result[i]
            result[i] = result[len(result) - 1 - i]
            result[len(result) - 1 - i] = temp
        return result
                    
    def isInputValid(self, userInput):
        if (userInput['startId'] > len(self.mapManager.getNodeDict(self.source[0], self.source[1]))) or (userInput['endId'] > len(self.mapManager.getNodeDict(self.destination[0], self.destination[1]))):
            print "Invalid input!"
            return False
        return True
    
    def clearMap(self):
        for i in range(0, self.maxXGrid):
            for j in range(0, self.maxYGrid):
                self.map[i][j] = 0
                self.obstacleMap[i][j] = False
                self.minDist[i][j] = self.INF
    
    def prepareRouteToNextPoint(self):
        if len(self.pathToGo) > 1:
            self.pathToGo.pop(0)
        if (len(self.pathToGo) > 1) and ((self.pathToGo[0][0] != self.pathToGo[1][0]) or (self.pathToGo[0][1] != self.pathToGo[1][1])):
            self.pathToGo.pop(0)
            self.curBuilding = self.pathToGo[0][0]
            self.curLevel = self.pathToGo[0][1]
            node = self.mapManager.getNode(self.pathToGo[0][0], self.pathToGo[0][1], self.pathToGo[0][2])
            self.curX = node.x
            self.curY = node.y
            self.mapHeading = self.mapManager.getMapHeading(self.pathToGo[0][0], self.pathToGo[0][1])
            
        if len(self.pathToGo) > 1:
            self.clearMap()
            node1 = self.mapManager.getNode(self.pathToGo[0][0], self.pathToGo[0][1], self.pathToGo[0][2])
            node2 = self.mapManager.getNode(self.pathToGo[1][0], self.pathToGo[1][1], self.pathToGo[1][2])
            
            self.drawRoute({'x':node1.x, 'y':node1.y}, {'x':node2.x, 'y':node2.y}, -1)
            self.mark({'x':node1.x, 'y':node1.y}, self.pathToGo[0][2])
            self.mark({'x':node2.x, 'y':node2.y}, self.pathToGo[1][2])

    def downloadMap(self, block, level):
        if self.mapManager.contains(block, level):
            return
        
        try:
            print "Downloading map", block, level
            mapDownload = urllib.URLopener()
            mapFileName = "XXLevelYY.json".replace("XX",str(block)).replace("YY",str(level))
            url = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=XX&Level=YY'.replace("XX", str(block)).replace("YY", str(level))
            mapDownload.retrieve(url, mapFileName)
            print "Finish downloading map", block, level
            #Load the downloaded json file into the program
            with open(mapFileName) as json_file:
                mapInfo = json.load(json_file)
                self.mapManager.addMap(block, level, mapInfo)
        except IOError:   
            print "Downloading map failed! Reading from cache..."
            with open(mapFileName) as json_file:    
                mapInfo = json.load(json_file)
                self.mapManager.addMap(block, level, mapInfo)
            
        nextMapList = self.mapManager.getNeighborMaps(block, level)
        for i in range(0, len(nextMapList)):
            self.downloadMap(nextMapList[i][0], nextMapList[i][1])
            
    def setStartAndEndPoint(self, userInput):
        self.curBuilding    = userInput['startBlock']
        self.curLevel       = userInput['startLevel']
        self.source         = (userInput['startBlock'], userInput['startLevel'], userInput['startId'])
        self.destination    = (userInput['endBlock'], userInput['endLevel'], userInput['endId'])
        
        self.downloadMap(self.curBuilding, self.curLevel)
        if self.mapManager.isMapValid(userInput['startBlock'], userInput['startLevel']) == False or self.mapManager.isMapValid(userInput['endBlock'], userInput['endLevel']) == False:
            return False
        
        if self.isInputValid(userInput) == False:
            return False
        
        self.mapHeading = self.mapManager.getMapHeading(userInput['startBlock'], userInput['startLevel'])
        self.startNode = self.mapManager.getNode(userInput['startBlock'], userInput['startLevel'], userInput['startId'])
        self.endNode = self.mapManager.getNode(userInput['endBlock'], userInput['endLevel'], userInput['endId'])
        self.curX = self.startNode.x
        self.curY = self.startNode.y
        self.pathToGo = self.dijkstra(self.startNode, self.endNode)
        print self.pathToGo
        
        self.pathToGo.insert(0, -1)
        self.prepareRouteToNextPoint()
        self.hasUpdate = True
        return True
    
    def printMap(self):
        os.system('clear')
        
        curX = int(self.curX / self.GRID_LENGTH)
        curY = int(self.curY / self.GRID_LENGTH)
        print "You are at", curX, curY,self.minDist[curX][curY]
        
        for i in range(-5,6):
            s = ""
            for j in range(-20,21):
                x = curX + j
                y = curY - i
                if (i==0) and (j==0):
                    s = s + 'Y'
                else:
                    if self.isValidPoint(x, y):
                        s = s + '.'
                    else :
                        s = s + 'X'
            print s
        #print "--------------------"
        #for i in range(-5,6):
        #    s = ""
        #    for j in range(-20,21):
        #        x = curX + j
        #        y = curY - i
        #        if (i==0) and (j==0):
        #            s = s + 'Y '
        #        else:
        #            if self.isValidPoint(x, y):
        #                if self.minDist[x][y] < self.INF:
        #                    s = s + str(self.minDist[x][y]) + " ";
        #                else :
        #                    s = s + "* "
        #            else :
        #                s = s + "X "
        #    print s
    
    def findDirectionToGo(self, realHeading, destHeading):
        diffAngle = min(abs(destHeading - realHeading), abs(realHeading - destHeading))
        print "find direction to go... real:", realHeading, "expect:", destHeading, "diff:", diffAngle
        if (diffAngle < self.ANGLE_LIMIT) :
            print "Go straight"
            if (AudioManager.isBusy() == False):
                AudioManager.play("straight_ahead")
        elif (realHeading + diffAngle + 360) % 360 == destHeading:
            print "Turn right " + str(realHeading) + " " + str((realHeading + diffAngle + 360) % 360) + " " + str(destHeading)
            if (AudioManager.isBusy() == False) :
                AudioManager.play("right")
        else :
            print "Turn left " + str(realHeading) + " " + str((realHeading - diffAngle + 360) % 360) + " " + str(destHeading)
            if (AudioManager.isBusy() == False) :
                AudioManager.play("left")
    
    def calculateDistanceToDestination(self, s):
        print "Recalculate distance"
        self.clearMinDist()
        
        queue = []
        sx = int(s.x/self.GRID_LENGTH)
        sy = int(s.y/self.GRID_LENGTH)
        self.minDist[sx][sy] = 0
        queue.append((sx, sy))
        
        while len(queue) > 0:
            u = queue.pop(0)
            for i in range(0, 8):
                v = (u[0] + self.nextDir[i][0], u[1] + self.nextDir[i][1])
                if self.isValidPoint(v[0], v[1]) and (self.minDist[v[0]][v[1]] == self.INF):
                    self.minDist[v[0]][v[1]] = self.minDist[u[0]][u[1]] + 1
                    queue.append(v)
        print "Finished recalculating distance"
    
    def getInstruction(self):
        if len(self.pathToGo) <= 1:
            print "No more node!"
            return
        
        if self.hasUpdate:
            self.calculateDistanceToDestination(self.mapManager.getNode(self.pathToGo[1][0], self.pathToGo[1][1], self.pathToGo[1][2]))
            self.hasUpdate = False
        
        realHeading = (self.mapHeading + self.curHeading) % 360
        #print realHeading
        curX = int(self.curX / self.GRID_LENGTH)
        curY = int(self.curY / self.GRID_LENGTH)
        
        # if cannot reach destination,
        if self.minDist[curX][curY] == self.INF:
            print "Path is blocked! Finding another path..."
            self.mapManager.blockPath(self.pathToGo[0][0], self.pathToGo[0][1], self.pathToGo[0][2], self.pathToGo[1][2])
            
            self.pathToGo = self.dijkstra(self.mapManager.getNode(self.pathToGo[0][0], self.pathToGo[0][1], self.pathToGo[0][2]), self.endNode)
            if (len(self.pathToGo) <= 1) or (self.pathToGo[-1] != self.endNode):
                print "You will never reach the destination!!!"
                return
            self.calculateDistanceToDestination(self.mapManager.getNode(self.pathToGo[0][0], self.pathToGo[0][1], self.pathToGo[0][2]))
        
        #print self.minDist[curX][curY]
        if (self.map[curX][curY] == self.pathToGo[1][2]): 
            print 'You have reached node' ,self.map[curX][curY]
            AudioManager.play('node')
            AudioManager.playNumber(self.map[curX][curY])
            self.prepareRouteToNextPoint()
            if len(self.pathToGo) <= 1:
                print "You reached the destination!"
                self.hasReachedDestination = True
                return
            self.calculateDistanceToDestination(self.mapManager.getNode(self.pathToGo[1][0], self.pathToGo[1][1], self.pathToGo[1][2]))
        
        #self.printMap()
        
        possibleHeading = []
        for i in range(0, 8):
            v = (curX + self.nextDir[i][0], curY + self.nextDir[i][1])
            #print v, self.minDist[v[0]][v[1]], self.minDist[curX][curY]
            if self.isValidPoint(v[0], v[1]) and (self.minDist[v[0]][v[1]] < self.minDist[curX][curY]):
                possibleHeading.append(self.nextDir[i][2])
                    
        if len(possibleHeading) > 0:
            chosenHeading = possibleHeading[0]
            for i in range(0, len(possibleHeading)):
                angleDiff1 = self.getAngleDifference(chosenHeading, realHeading)
                angleDiff2 = self.getAngleDifference(possibleHeading[i], realHeading)
                if angleDiff2 < angleDiff1:
                    chosenHeading = possibleHeading[i]
            
            self.findDirectionToGo(realHeading, chosenHeading)
        else:
            print "Cannot find any direction! Try to turn right..."
            if (AudioManager.isBusy() == False) :
                AudioManager.play("right")
            
    def getAngleDifference(self, theta1, theta2):
        angleDiff = abs(theta1 - theta2)
        if (angleDiff > 180) :
            angleDiff = 360 - angleDiff
        return angleDiff
            
    def markObstacle(self, x, y, value):
        if self.isInsideMapGrid(x, y) and (self.obstacleMap[x][y] != value):
            self.obstacleMap[x][y] = value
            return 1
        return 0
    
    def getNeighbor(self, x, y, heading):
        chosenAngle = 0
        for i in range(0, 8):
            if self.getAngleDifference(self.nextDir[chosenAngle][2], heading) > self.getAngleDifference(self.nextDir[i][2], heading):
                chosenAngle = i
        return (x + self.nextDir[chosenAngle][0], y + self.nextDir[chosenAngle][1])
        
    
    def putObstacle(self, heading):
        realHeading = (self.mapHeading + self.curHeading + heading + 360)%360
        x, y = self.getNeighbor(int(self.curX/self.GRID_LENGTH), int(self.curY/self.GRID_LENGTH), realHeading)
        temp = self.markObstacle(x, y, True)
        if (temp > 0):
            print "Put obstacle", heading
            self.hasUpdate = True
    
    def removeObstacle(self, heading):
        realHeading = (self.mapHeading + self.curHeading + heading + 360)%360
        x, y = self.getNeighbor(int(self.curX/self.GRID_LENGTH), int(self.curY/self.GRID_LENGTH), realHeading)
        temp = self.markObstacle(x, y, False)
        if (temp > 0):
            print "Removed obstacle", heading
            self.hasUpdate = True
    
if __name__ == '__main__':
    AudioManager.init()
    gridMapNavigator = GridMapNavigator()
    if gridMapNavigator.setStartAndEndPoint({'startBlock' : 1, 'startLevel' : 2, 'startId' : 1,
                                             'endBlock' : 2, 'endLevel' : 3, 'endId' : 6}):
        gridMapNavigator.curX = 0
        gridMapNavigator.curY = 2436
        gridMapNavigator.curHeading = 135
        gridMapNavigator.putObstacle(0)
        gridMapNavigator.putObstacle(-45)
        gridMapNavigator.putObstacle(45)
        gridMapNavigator.getInstruction()
    else :
        print "setStartAndEndPoint failed"