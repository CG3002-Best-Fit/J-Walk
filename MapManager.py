'''
Created on Nov 6, 2015

@author: bamboo3250
'''
class Node(object):
    def getPos(self):
        return {'x':self.x, 'y':self.y}
    
    def __init__(self, block, level, nodeInfo):
        self.block = block
        self.level = level
        self.nodeId = int(nodeInfo['nodeId'])
        self.code = str(self.block) + "-" + str(self.level) + "-" + str(self.nodeId)
        self.x = int(nodeInfo['x'])
        self.y = int(nodeInfo['y'])
        self.specialLinkTo = None
        self.nodeName = nodeInfo['nodeName']
        nodeNameParams = self.nodeName.split(' ')
        if (len(nodeNameParams) == 2) and (nodeNameParams[0] == 'TO'):
            specialNextNodeNameParams = nodeNameParams[1].split('-')
            if len(specialNextNodeNameParams) == 3:
                nextBlock = int(specialNextNodeNameParams[0])
                nextLevel = int(specialNextNodeNameParams[1])
                nextId = int(specialNextNodeNameParams[2])
                self.specialLinkTo = (nextBlock, nextLevel, nextId) 
        
        self.linkTo = nodeInfo['linkTo'].replace(' ','').split(",")
        for i in range(0, len(self.linkTo)):
            self.linkTo[i] = int(self.linkTo[i])

class Map(object):
    def getMapName(self):
        return str(self.block) + "-" + str(self.level)
    
    def getNeighborMaps(self):
        result = []
        for i in self.nodeDict:
            node = self.nodeDict[i]
            if node.specialLinkTo != None:
                result.append((node.specialLinkTo[0], node.specialLinkTo[1]))
        return result
    
    def getNode(self, nodeId):
        if self.nodeDict.has_key(nodeId):
            return self.nodeDict[nodeId]
        else:
            return None
    
    def canPass(self, id1, id2):
        if (self.canPassDict[id1] == None):
            return False
        if (self.canPassDict[id1][id2] == None):
            return False
        return self.canPassDict[id1][id2]
    
    def blockPath(self, id1, id2):
        self.canPassDict[id1][id2] = False
        self.canPassDict[id2][id1] = False
    
    def __init__(self, block, level, mapInfo):
        self.block = block
        self.level = level
        self.nodeDict = {}
        self.canPassDict = {}
        
        if mapInfo['info'] != None:
            self.northAt = int(mapInfo['info']['northAt'])
        for nodeInfo in mapInfo['map']:
            newNode = Node(self.block, self.level, nodeInfo)
            self.nodeDict[newNode.nodeId] = newNode
            self.canPassDict[newNode.nodeId] = {}
            for v in newNode.linkTo:
                self.canPassDict[newNode.nodeId][v] = True

class MapManager(object):
    def getMap(self, block, level):
        mapName = str(block) + "-" + str(level)
        if (self.mapDict.has_key(mapName)) :
            return self.mapDict[mapName]
        else:
            return None
    
    def contains(self, block, level):
        return self.getMap(block, level) != None
    
    def addMap(self, block, level, mapInfo):
        newMap = Map(block, level, mapInfo)
        self.mapDict[newMap.getMapName()] = newMap
        
    def getNeighborMaps(self, block, level):
        return self.getMap(block, level).getNeighborMaps()
    
    def getNode(self, block, level, nodeId):
        return self.getMap(block, level).getNode(nodeId)
    
    def getNodeDict(self, block, level):
        mapName = str(block) + "-" + str(level)
        return self.mapDict[mapName].nodeDict
    
    def getMapHeading(self, block, level):
        return self.getMap(block, level).northAt
    
    def isMapValid(self, block, level):
        if (len(self.getMap(block, level).nodeDict) == 0) : #map doesn't exist
            print "Map", block, level, "doesn't exist"
            return False
        return True
    
    def canPass(self, block, level, id1, id2):
        return self.getMap(block, level).canPass(id1, id2)
    
    def blockPath(self, block, level, id1, id2):
        self.getMap(block, level).blockPath(id1, id2)
        
    def __init__(self):
        self.mapDict = {}