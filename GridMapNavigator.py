'''
Created on Oct 23, 2015

@author: bamboo3250
'''
import urllib
import json
import math 
import AudioManager
import os

class GridMapNavigator(object):
    map = []
    obstacleMap = []
    minDist = []
    mapHeading = 0
    startNode = {}
    endNode = {}
    curBuilding = 1
    curLevel = 2
    curX = 0 
    curY = 0
    curHeading = 0
    notifiedReachNode = False
    
    ANGLE_LIMIT = 15
    INF = 1000000000
    STEP_LENGTH = 42
    GRID_LENGTH = 50
    maxXGrid = 0
    maxYGrid = 0
    
    hasUpdate = False
    nextDir = [[0,1,0],[1,1,45],[1,0,90],[1,-1,135],[0,-1, 180],[-1,-1, 225],[-1, 0, 270],[-1,1, 315]]
    
    def getCurrentBuilding(self):
        return self.curBuilding
    
    def getCurrentLevel(self):
        return self.curLevel
    
    def setHeading(self, value):
        self.curHeading = value
    
    def getCurrentPos(self):
        return [self.curX, self.curY, self.curHeading]
    
    def stepAhead(self, numSteps):
        totalHeading = 90 - (self.curHeading + self.mapHeading)
        self.curX = max(0, self.curX + numSteps * self.STEP_LENGTH * math.cos(math.radians(totalHeading)));
        self.curY = max(0, self.curY + numSteps * self.STEP_LENGTH * math.sin(math.radians(totalHeading)));
    
    
    def downloadMap(self, block, level):
        try:
            mapDownload = urllib.URLopener()
            mapName = "XXLevelYY.json"
            
            url = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=XX&Level=YY'
            url = url.replace("XX", str(block))
            url = url.replace("YY", str(level))
            mapName = mapName.replace("XX",str(block))
            mapName = mapName.replace("YY",str(level))
            mapDownload.retrieve(url, mapName)
        
            #Load the downloaded json file into the program
            with open(mapName) as json_file:    
                mapInfo = json.load(json_file)
            return mapInfo
        except IOError:   
            with open(mapName) as json_file:    
                mapInfo = json.load(json_file)
            return mapInfo
    
    def __init__(self):
        pass
    
    def extractMap(self, nodeList):
        nodeDict = {}
        for node in nodeList:
            node['nodeId'] = int(node['nodeId'])
            node['x'] = int(node['x'])
            node['y'] = int(node['y'])
            node['linkTo'] = node['linkTo'].replace(' ','').split(",")
            for i in range(0, len(node['linkTo'])):
                node['linkTo'][i] = int(node['linkTo'][i])
            
            nodeDict[node['nodeId']] = node
        return nodeDict
    
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
    
    def drawRoute(self, s, t):
        length = self.dist(s,t)
        direction = [(t['x'] - s['x']) / length*self.GRID_LENGTH, (t['y'] - s['y']) / length*self.GRID_LENGTH]    # 1 meter
        u = dict(s)
        count = 0
        while self.dist(u, t) >= self.GRID_LENGTH:
            #print str(u['x']) + " " + str(u['y']) + " " + str(count)
            self.mark(u, -1)
            count = count + 1
            u['x'] = int(s['x'] + direction[0] * count)
            u['y'] = int(s['y'] + direction[1] * count)
            #print str(u['x']) + "->" + str(s['x']) + " " + str(count) + " " + str(direction[0] * count)
            
    
    def create2DArray(self, n, m, initValue):
        return [[initValue for i in range(n)] for j in range(m)]
    
    def initGridMap(self, nodeDict):
        self.maxXGrid = 200*100/self.GRID_LENGTH
        self.maxYGrid = 200*100/self.GRID_LENGTH
        self.map = self.create2DArray(self.maxYGrid, self.maxXGrid, 0)
        print "finish map"
        self.minDist = self.create2DArray(self.maxYGrid, self.maxXGrid, 0)
        print "finish minDist"
        self.obstacleMap = self.create2DArray(self.maxYGrid, self.maxXGrid, True)
        print "finish obstacleMap"
        
        #print nodeDict
        for u in nodeDict.keys():
            u = nodeDict[u]
            for i in u['linkTo']:
                v = nodeDict[i]
                self.drawRoute(u, v)
        print "finish draw route"
        
        for i in nodeDict:
            node = nodeDict[i]
            self.mark(node, int(node['nodeId']))
        print "finish mark"
    
    def calculateDistanceToDestination(self, s):
        print "Recalculate distance"
        print s
        for i in range(0, self.maxXGrid):
            for j in range(0, self.maxYGrid):
                self.minDist[i][j] = self.INF
        
        queue = []
        sx = int(s['x']/self.GRID_LENGTH)
        sy = int(s['y']/self.GRID_LENGTH)
        self.minDist[sx][sy] = 0
        queue.append((sx, sy))
        
        nextDir = [[0,1],[1,0],[-1,0],[0,-1],[-1,1],[1,-1],[1,1],[-1,-1]]
        
        while len(queue) > 0:
            u = queue.pop(0)
            for i in range(0, 8):
                v = (u[0] + nextDir[i][0], u[1] + nextDir[i][1])
                if self.isInsideMapGrid(v[0], v[1]) and (self.map[v[0]][v[1]] != 0) and (self.obstacleMap[v[0]][v[1]] == False):
                    if self.minDist[v[0]][v[1]] == self.INF:
                        self.minDist[v[0]][v[1]] = self.minDist[u[0]][u[1]] + 1
                        queue.append(v)
    
    def setStartAndEndPoint(self, userInput):
        print "download map"
        mapInfo = self.downloadMap(userInput[0], userInput[1])
        self.curBuilding = userInput[0]
        self.curLevel = userInput[1]
        print "finish download map"
        
        if (mapInfo['info'] == None) : #map doesn't exist
            print "map doesn't exist"
            return False
        else :
            print "extract map"
            self.mapHeading = int(mapInfo['info']['northAt'])
            
            nodeDict = self.extractMap(mapInfo['map'])
            print "init grid"
            self.initGridMap(nodeDict)
            
            if (userInput[2] > len(nodeDict)) or (userInput[5] > len(nodeDict)):
                print "invalid input"
                return False
            
            self.startNode = nodeDict[userInput[2]]
            self.endNode = nodeDict[userInput[5]]
            
            self.curX = self.startNode['x']
            self.curY = self.startNode['y']
            
            print "BFS"
            self.calculateDistanceToDestination(self.endNode)
            return True
    
    def printMap(self):
        os.system('clear')
        
        curX = int(self.curX / self.GRID_LENGTH)
        curY = int(self.curY / self.GRID_LENGTH)
        
        for i in range(-5,11):
            s = ""
            for j in range(-5,11):
                x = curX + j
                y = curY - i
                if self.isInsideMapGrid(x, y) and (self.map[x][y] != 0) and (self.obstacleMap[x][y] == False):
                    if (i==0) and (j==0):
                        s = s + 'Y'
                    else:
                        s = s + '.'
                else :
                    s = s + 'X'
            print s
    
    def findDirectionToGo(self, realHeading, destHeading):
        print "find direction to go..."
        diffAngle = min(abs(destHeading - realHeading + 360)%360, abs(realHeading - destHeading + 360)%360)
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
        
        if self.hasUpdate:
            self.calculateDistanceToDestination(self.endNode)
            self.hasUpdate = False
        
        realHeading = (self.mapHeading + self.curHeading) % 360
        #print realHeading
        
        curX = int(self.curX / self.GRID_LENGTH)
        curY = int(self.curY / self.GRID_LENGTH)
        
        #print self.minDist[curX][curY]
        if self.isInsideMapGrid(curX, curY) and (self.map[curX][curY] != 0) and (self.minDist[curX][curY] < self.INF):
            #nextDir = [[0,1,0],[1,1,45],[1,0,90],[1,-1,135],[0,-1, 180],[-1,-1, 225],[-1, 0, 270],[-1,1, 315]]
            if (self.map[curX][curY] != -1): 
                if (self.notifiedReachNode == False):
                    print 'You have reached node' ,self.map[curX][curY]
                    AudioManager.play('node')
                    AudioManager.playNumber(self.map[curX][curY])
                    self.notifiedReachNode = True
                    if self.map[curX][curY] == self.endNode['nodeId']:
                        return False
            else :
                self.notifiedReachNode = False
            
            possibleHeading = []
            for i in range(0, 8):
                v = (curX + self.nextDir[i][0], curY + self.nextDir[i][1])
                if self.isInsideMapGrid(v[0], v[1]) and (self.map[v[0]][v[1]] != 0):
                    if self.minDist[v[0]][v[1]] + 1 == self.minDist[curX][curY]:
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
            return True
            
        else :
            print "Invalid current point! Go to the nearest valid point"
            #self.removeObstacle(0)
            angleToGo = self.findDirectionToNearestValidPoint(curX, curY, realHeading)
            self.findDirectionToGo(realHeading, angleToGo)
            return True
            
    def getAngleDifference(self, theta1, theta2):
        angleDiff = abs(theta1 - theta2)
        if (angleDiff > 180) :
            angleDiff = 360 - angleDiff
        return angleDiff
            
    def findDirectionToNearestValidPoint(self, x, y, curHeading):
        count = 0
        #nextDir = [[0,1,0],[1,1,45],[1,0,90],[1,-1,135],[0,-1, 180],[-1,-1, 225],[-1, 0, 270],[-1,1, 315]]
        print "find nearest valid point"
        while count < 10:
            print "count = " + str(count)
            possibleHeading = []
            for i in range(8):
                v = (x + self.nextDir[i][0]*count, y + self.nextDir[i][1]*count)
                print v
                print str(self.map[v[0]][v[1]]) + " " + str(self.minDist[v[0]][v[1]]) + " " + str(self.obstacleMap[v[0]][v[1]])
                if self.isInsideMapGrid(v[0], v[1]) and (self.map[v[0]][v[1]] != 0) and (self.minDist[v[0]][v[1]] < self.INF) and (self.obstacleMap[v[0]][v[1]] == False):
                    possibleHeading.append(self.nextDir[i][2])
                    print "append " + str(self.nextDir[i][2])
            print "finish check 8 directions"
            if len(possibleHeading) > 0:
                chosenHeading = possibleHeading[0]
                for i in range(0, len(possibleHeading)):
                    angleDiff1 = self.getAngleDifference(chosenHeading, curHeading)
                    angleDiff2 = self.getAngleDifference(possibleHeading[i], curHeading)
                    if angleDiff2 < angleDiff1:
                        chosenHeading = possibleHeading[i]
                return chosenHeading
            count = count + 1
    
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
            self.hasUpdate = True
    
    def removeObstacle(self, heading):
        realHeading = (self.mapHeading + self.curHeading + heading + 360)%360
        x, y = self.getNeighbor(int(self.curX/self.GRID_LENGTH), int(self.curY/self.GRID_LENGTH), realHeading)
        temp = self.markObstacle(x, y, False)
        if (temp > 0):
            self.hasUpdate = True
    
if __name__ == '__main__':
    AudioManager.init()
    gridMapNavigator = GridMapNavigator()
    if gridMapNavigator.setStartAndEndPoint([1,2,1,1,2,11]):
        gridMapNavigator.curX = 0
        gridMapNavigator.curY = 2436
        gridMapNavigator.curHeading = 50
        gridMapNavigator.putObstacle(50)
        gridMapNavigator.getInstruction()
    else :
        print "setStartAndEndPoint failed"