'''
Created on Oct 23, 2015

@author: bamboo3250
'''
import urllib
import json
import math 
import AudioManager

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
    notifiedReachNode = False;
    
    
    STEP_LENGTH = 5
    
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
        for node in nodeList:
            node['x'] = int(node['x'])/10
            node['y'] = int(node['y'])/10
            node['linkTo'] = node['linkTo'].replace(' ','').split(",")
            for i in range(0, len(node['linkTo'])):
                node['linkTo'][i] = int(node['linkTo'][i]) - 1
        return nodeList
    
    def dist(self, u, v):
        dir = [v['x'] - u['x'], v['y'] - u['y']]
        return math.sqrt(math.pow(dir[0],2) + math.pow(dir[1],2))
    
    def mark(self, u, value):
        for i in range(-5, 11):
            for j in range(-5, 11):
                x = u['x'] + i
                y = u['y'] + j
                if (0 <= x) and (x < 2000) and (0 <= y) and (y < 2000):
                    self.map[x][y] = value
                    if (value != 0) :
                        self.obstacleMap[x][y] = False
    
    def markObstacle(self, u, value):
        count = 0
        for i in range(-3, 7):
            for j in range(-3, 7):
                x = u['x'] + i
                y = u['y'] + j
                if (0 <= x) and (x < 2000) and (0 <= y) and (y < 2000) and (self.obstacleMap[x][y] != value):
                    count = count + 1
                    self.obstacleMap[x][y] = value
        return count
    
    def drawRoute(self, s, t):
        length = self.dist(s,t)
        direction = [(t['x'] - s['x']) / length, (t['y'] - s['y']) / length]
        u = dict(s)
        count = 0
        while self.dist(u, t) > 2:
            #print str(u['x']) + " " + str(u['y']) + " " + str(count)
            self.mark(u, -1)
            #self.markObstacle(u, False)
            count = count + 1
            u['x'] = int(s['x'] + direction[0] * count)
            u['y'] = int(s['y'] + direction[1] * count)
            #print str(u['x']) + "->" + str(s['x']) + " " + str(count) + " " + str(direction[0] * count)
            
    
    def initGridMap(self, adjList):
        self.map = [[0 for i in range(2000)] for j in range(2000)]
        print "finish map"
        self.minDist = [[0 for i in range(2000)] for j in range(2000)]
        print "finish minDist"
        self.obstacleMap = [[True for i in range(2000)] for j in range(2000)]
        print "finish obstacleMap"
        
        for u in adjList:
            for i in u['linkTo']:
                v = adjList[i]
                self.drawRoute(u, v)
        print "finish draw route"
        
        for node in adjList:
            self.mark(node, int(node['nodeId']))
        print "finish mark"
    
    def BFS(self, s):
        for i in range(0, 2000):
            for j in range(0, 2000):
                self.minDist[i][j] = 1000000000
                  
        
        queue = []
        self.minDist[s['x']][s['y']] = 0
        queue.append((s['x'], s['y']))
        
        nextDir = [[0,1],[1,0],[-1,0],[0,-1],[-1,1],[1,-1],[1,1],[-1,-1]]
        
        while len(queue) > 0:
            u = queue.pop(0)
            #print str(u[0]) + " " + str(u[1])
            for i in range(0, 8):
                v = (u[0] + nextDir[i][0], u[1] + nextDir[i][1])
                #print v
                #print self.minDist[v[0]][v[1]]
                if (0 <= v[0]) and (v[0] < 2000) and (0 <= v[1]) and (v[1] < 2000) and (self.map[v[0]][v[1]] != 0) and (self.obstacleMap[v[0]][v[1]] == False):
                    if self.minDist[v[0]][v[1]] == 1000000000:
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
            
            adjList = self.extractMap(mapInfo['map'])
            print "init grid"
            self.initGridMap(adjList)
            
            if (userInput[2] > len(adjList)) or (userInput[5] > len(adjList)):
                return False
            
            self.startNode = adjList[userInput[2]-1]
            self.endNode = adjList[userInput[5]-1]
            
            self.curX = self.startNode['x']
            self.curY = self.startNode['y']
            
            print "BFS"
            self.BFS(self.endNode)
            return True
            
    def getInstruction(self):
        ANGLE_LIMIT = 15
        
        realHeading = (self.mapHeading + self.curHeading) % 360
        print realHeading
        
        print self.minDist[self.curX][self.curY]
        if (0 <= self.curX) and (self.curX < 2000) and (0 <= self.curY) and (self.curY < 2000) and (self.map[self.curX][self.curY] != 0) and (self.minDist[self.curX][self.curY] < 1000000000):
            nextDir = [[0,1,0],[1,1,45],[1,0,90],[1,-1,135],[0,-1, 180],[-1,-1, 225],[-1, 0, 270],[-1,1, 315]]
            if (self.map[self.curX][self.curY] != -1): 
                if (self.notifiedReachNode == False):
                    print 'You have reached node' ,self.map[self.curX][self.curY]
                    AudioManager.play('node')
                    AudioManager.playNumber(self.map[self.curX][self.curY])
                    self.notifiedReachNode = True
            else :
                self.notifiedReachNode = False
            
            for i in range(0, 8):
                v = (self.curX + nextDir[i][0], self.curY + nextDir[i][1])
                print v
                print str(self.minDist[v[0]][v[1]]) + " " + str(self.minDist[self.curX][self.curY])
                if (0 <= v[0]) and (v[0] < 2000) and (0 <= v[1]) and (v[1] < 2000) and (self.map[v[0]][v[1]] != 0):
                    if self.minDist[v[0]][v[1]] + 1 == self.minDist[self.curX][self.curY]:
                        destHeading = nextDir[i][2]
                        
                        diffAngle = min(abs(destHeading - realHeading + 360)%360, abs(realHeading - destHeading + 360)%360)
                        if (diffAngle < ANGLE_LIMIT) :
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
                                
                        #print "Go to " + str(nextDir[i][0]) + " " + str(nextDir[i][1])
                        return 
        else :
            print "Invalid current point"
            
    def putObstacle(self, heading):
        realHeading = (self.mapHeading + self.curHeading + heading + 360)%360
        headingInRad = math.radians(realHeading)
        v = {}
        v['x'] = int(self.curX + 5*math.sin(headingInRad))
        v['y'] = int(self.curY + 5*math.cos(headingInRad))
        
        temp = self.markObstacle(v, True)
        if (temp > 0):
            self.BFS(self.endNode)
    
    def removeObstacle(self, heading):
        realHeading = (self.mapHeading + self.curHeading + heading + 360)%360
        headingInRad = math.radians(realHeading)
        s = {}
        s['x'] = self.curX
        s['y'] = self.curY
        
        v = {}
        v['x'] = int(self.curX + 5*math.sin(headingInRad))
        v['y'] = int(self.curY + 5*math.cos(headingInRad))
        
        length = self.dist(s,v)
        direction = [(v['x'] - s['x']) / length, (v['y'] - s['y']) / length]
        u = dict(s)
        count = 0
        temp = 0
        while self.dist(u, v) > 2:
            #print str(u['x']) + " " + str(u['y']) + " " + str(count)
            temp = temp + self.markObstacle(v, False)
            count = count + 1
            u['x'] = int(s['x'] + direction[0] * count)
            u['y'] = int(s['y'] + direction[1] * count)
        
        if (temp > 0):
            self.BFS(self.endNode)
    
if __name__ == '__main__':
    gridMapNavigator = GridMapNavigator()
    if gridMapNavigator.setStartAndEndPoint([1,2,13,1,2,16]):
        #gridMapNavigator.putObstacle(556, 90, 45)
        gridMapNavigator.curX = 556
        gridMapNavigator.curY = 90
        gridMapNavigator.curHeading = 90
        gridMapNavigator.getInstruction()
    else :
        print "setStartAndEndPoint failed"
                                          