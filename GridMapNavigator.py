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

class GridMapNavigator(object):
    map = []
    obstacleMap = []
    minDist = []
    mapHeading = 0
    startNode = {}
    endNode = {}
    nodeDict = {}
    canPass = {}
    
    curBuilding = 1
    curLevel = 2
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
    
    def downloadMap(self, block, level):
        try:
            print "Downloading map"
            
            mapDownload = urllib.URLopener()
            mapName = "XXLevelYY.json"
            
            url = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=XX&Level=YY'
            url = url.replace("XX", str(block))
            url = url.replace("YY", str(level))
            mapName = mapName.replace("XX",str(block))
            mapName = mapName.replace("YY",str(level))
            mapDownload.retrieve(url, mapName)
            
            print "Finish downloading map"
            #Load the downloaded json file into the program
            with open(mapName) as json_file:    
                mapInfo = json.load(json_file)
            return mapInfo
        except IOError:   
            print "Downloading map failed! Reading from cache..."
            with open(mapName) as json_file:    
                mapInfo = json.load(json_file)
            return mapInfo
    
    def __init__(self):
        self.maxXGrid = 200*100/self.GRID_LENGTH
        self.maxYGrid = 200*100/self.GRID_LENGTH
        self.map = self.create2DArray(self.maxYGrid, self.maxXGrid, 0)
        print "finish creating map"
        self.minDist = self.create2DArray(self.maxYGrid, self.maxXGrid, 0)
        print "finish creating minDist"
        self.obstacleMap = self.create2DArray(self.maxYGrid, self.maxXGrid, True)
        print "finish creating obstacleMap"
        
        self.canPass = {}
        for i in range(1, 100):
            self.canPass[i] = {}
            for j in range(1, 100):
                self.canPass[i][j] = False
    
    def extractMap(self, nodeList):
        print "Extracting map"
        self.nodeDict = {}
        for node in nodeList:
            node['nodeId'] = int(node['nodeId'])
            node['x'] = int(node['x'])
            node['y'] = int(node['y'])
            node['linkTo'] = node['linkTo'].replace(' ','').split(",")
            for i in range(0, len(node['linkTo'])):
                node['linkTo'][i] = int(node['linkTo'][i])
                self.canPass[node['nodeId']][node['linkTo'][i]] = True
                self.canPass[node['linkTo'][i]][node['nodeId']] = True
            
            self.nodeDict[node['nodeId']] = node
    
    def dist(self, u, v):
        return math.sqrt(math.pow(v['x'] - u['x'],2) + math.pow(v['y'] - u['y'],2))
    
    def isInsideMapGrid(self, x, y):
        return (0 <= x) and (x < self.maxXGrid) and (0 <= y) and (y < self.maxYGrid)
    
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
            
    
    def create2DArray(self, n, m, initValue):
        return [[initValue for i in range(n)] for j in range(m)]
    
    def clearMinDist(self):
        print "Clearing minDist"
        if len(self.pathToGo) > 1:
            minX = min(self.nodeDict[self.pathToGo[0]]['x'], self.nodeDict[self.pathToGo[1]]['x']) - 2
            maxX = max(self.nodeDict[self.pathToGo[0]]['x'], self.nodeDict[self.pathToGo[1]]['x']) + 2
            minY = min(self.nodeDict[self.pathToGo[0]]['y'], self.nodeDict[self.pathToGo[1]]['y']) - 2
            maxY = max(self.nodeDict[self.pathToGo[0]]['y'], self.nodeDict[self.pathToGo[1]]['y']) + 2
            for i in range(minX, maxX + 1):
                for j in range(minY, maxY + 1):
                    if self.isInsideMapGrid(i, j):
                        self.minDist[i][j] = self.INF
        print "Finished clearing minDist"
    
    def calculateDistanceToDestination(self, s):
        print "Recalculate distance"
        self.clearMinDist()
        
        queue = []
        sx = int(s['x']/self.GRID_LENGTH)
        sy = int(s['y']/self.GRID_LENGTH)
        self.minDist[sx][sy] = 0
        queue.append((sx, sy))
        
        while len(queue) > 0:
            u = queue.pop(0)
            #print u, self.minDist[u[0]][u[1]]
            for i in range(0, 8):
                v = (u[0] + self.nextDir[i][0], u[1] + self.nextDir[i][1])
                if self.isValidPoint(v[0], v[1]) and (self.minDist[v[0]][v[1]] == self.INF):
                    self.minDist[v[0]][v[1]] = self.minDist[u[0]][u[1]] + 1
                    queue.append(v)
        print "Finished recalculating distance"
    
    def dijkstra(self, s, t):
        d = {}
        parent = {}
        for i in self.nodeDict:
            d[i] = self.INF
        d[s] = 0
        parent[s] = -1
        priority_queue = [(d[i], i) for i in self.nodeDict]
        heapq.heapify(priority_queue)
    
        while len(priority_queue) > 0:
            pair = heapq.heappop(priority_queue)
            u = pair[1]
            if pair[0] != d[u]:
                continue
            if u == t:
                break
            
            for i in range(0, len(self.nodeDict[u]['linkTo'])):
                v = self.nodeDict[u]['linkTo'][i]
                w = self.dist(self.nodeDict[u], self.nodeDict[v])
                if self.canPass[u][v] and d[v] > d[u] + w:
                    parent[v] = u
                    d[v] = d[u] + w
                    heapq.heappush(priority_queue, (d[v],v))
        
        result = []
        temp = self.endNode['nodeId']
        while temp != -1:
            result.append(temp)
            temp = parent[temp]
        for i in range(0, len(result)/2):
            temp = result[i]
            result[i] = result[len(result) - 1 - i]
            result[len(result) - 1 - i] = temp
        return result
                    
    def isMapValid(self, mapInfo):
        if (mapInfo['info'] == None) : #map doesn't exist
            print "Map doesn't exist"
            return False
        return True
        
    def isInputValid(self, userInput):
        if (userInput['startId'] > len(self.nodeDict)) or (userInput['endId'] > len(self.nodeDict)):
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
            if len(self.pathToGo) > 1:
                self.clearMap()
                self.drawRoute(self.nodeDict[self.pathToGo[0]], self.nodeDict[self.pathToGo[1]], -1)
                self.mark(self.nodeDict[self.pathToGo[0]], self.pathToGo[0])
                self.mark(self.nodeDict[self.pathToGo[1]], self.pathToGo[1])
    
    def setStartAndEndPoint(self, userInput):
        self.curBuilding = userInput['startBlock']
        self.curLevel = userInput['startLevel']
        
        mapInfo = self.downloadMap(self.curBuilding, self.curLevel)
        if self.isMapValid(mapInfo) == False:
            return False
        
        self.extractMap(mapInfo['map'])
        if self.isInputValid(userInput) == False:
            return False
        
        self.mapHeading = int(mapInfo['info']['northAt'])
        self.startNode = self.nodeDict[userInput['startId']]
        self.endNode = self.nodeDict[userInput['endId']]
        self.curX = self.startNode['x']
        self.curY = self.startNode['y']
        self.pathToGo = self.dijkstra(userInput['startId'], userInput['endId'])
        print self.pathToGo
        self.pathToGo.insert(0, -1)
        self.prepareRouteToNextPoint()
        self.hasUpdate = True
        return True
    
    def printMap(self):
        os.system('clear')
        
        curX = int(self.curX / self.GRID_LENGTH)
        curY = int(self.curY / self.GRID_LENGTH)
        
        for i in range(-5,6):
            s = ""
            for j in range(-30,31):
                x = curX + j
                y = curY - i
                if (i==0) and (j==0):
                    s = s + 'Y'
                else:
                    if self.isInsideMapGrid(x, y) and (self.map[x][y] != 0) and (self.obstacleMap[x][y] == False):
                        s = s + '.'
                    else :
                        s = s + 'X'
            print s
    
    def findDirectionToGo(self, realHeading, destHeading):
        diffAngle = min(abs(destHeading - realHeading), abs(realHeading - destHeading))
        print "find direction to go...", realHeading, destHeading, diffAngle
        if (diffAngle < self.ANGLE_LIMIT) :
            print "Go straight"
            if (AudioManager.isBusy() == False):
                AudioManager.play("straight_ahead")
        else :
            if (realHeading + diffAngle + 360) % 360 == destHeading:
                print "Turn right " + str(realHeading) + " " + str((realHeading + diffAngle + 360) % 360) + " " + str(destHeading)
                if (AudioManager.isBusy() == False) :
                    AudioManager.play("right")
            else :
                print "Turn left " + str(realHeading) + " " + str((realHeading + diffAngle + 360) % 360) + " " + str(destHeading)
                if (AudioManager.isBusy() == False) :
                    AudioManager.play("left")
    
    def getInstruction(self):
        self.printMap()
        
        if len(self.pathToGo) <= 1:
            print "No more node!"
            return
        
        if self.hasUpdate:
            self.calculateDistanceToDestination(self.nodeDict[self.pathToGo[1]])
            self.hasUpdate = False
        
        realHeading = (self.mapHeading + self.curHeading) % 360
        #print realHeading
        curX = int(self.curX / self.GRID_LENGTH)
        curY = int(self.curY / self.GRID_LENGTH)
        
        # if cannot reach destination,
        if self.minDist[curX][curY] == self.INF:
            print "Path is blocked! Finding another path..."
            self.canPass[self.pathToGo[0]][self.pathToGo[1]] = False
            self.canPass[self.pathToGo[1]][self.pathToGo[0]] = False
            self.pathToGo = self.dijkstra(self.pathToGo[0], self.endNode['nodeId'])
            if (len(self.pathToGo) <= 1) or (self.pathToGo[-1] != self.endNode['nodeId']):
                print "You will never reach the destination!!!"
                return
            self.calculateDistanceToDestination(self.nodeDict[self.pathToGo[0]])
        
        #print self.minDist[curX][curY]
        if (self.map[curX][curY] == self.pathToGo[1]): 
            print 'You have reached node' ,self.map[curX][curY]
            AudioManager.play('node')
            AudioManager.playNumber(self.map[curX][curY])
            self.prepareRouteToNextPoint()
            if len(self.pathToGo) <= 1:
                print "You reached the destination!"
                self.hasReachedDestination = True
                return
            self.calculateDistanceToDestination(self.nodeDict[self.pathToGo[1]])
            
        
        possibleHeading = []
        for i in range(0, 8):
            v = (curX + self.nextDir[i][0], curY + self.nextDir[i][1])
            #print v, self.minDist[v[0]][v[1]], self.minDist[curX][curY]
            if self.isValidPoint(v[0], v[1]) and (self.minDist[v[0]][v[1]] + 1 == self.minDist[curX][curY]):
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
            print "cannot find any direction"
        return
            
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
                                             'endBlock' : 1, 'endLevel' : 2, 'endId' : 11}):
        gridMapNavigator.curX = 0
        gridMapNavigator.curY = 2436
        gridMapNavigator.curHeading = 135
        gridMapNavigator.putObstacle(0)
        gridMapNavigator.putObstacle(-45)
        gridMapNavigator.getInstruction()
    else :
        print "setStartAndEndPoint failed"