'''
Created on Oct 23, 2015

@author: bamboo3250
'''
import urllib
import json

class GridMapNavigator(object):
    map = []
    
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
        adjList = []
        for node in nodeList:
            node['x'] = int(node['x'])/10
            node['y'] = int(node['y'])/10
            node['linkTo'] = node['linkTo'].replace(' ','').split(",")
            for i in range(0, len(node['linkTo'])):
                node['linkTo'][i] = int(node['linkTo'][i]) - 1
            adjList.append(node)
        return adjList
    
    def setStartAndEndPoint(self, userInput):
        mapInfo = self.downloadMap(userInput[0], userInput[1])
        if (mapInfo['info'] == None) : #map doesn't exist
            return False
        else :
            self.map = []
            for i in range(0, 2000):
                self.map.append([])
                for j in range(0, 2000):
                    self.map[i].append(0)
            
            adjList = self.extractMap(mapInfo['map'])
            

if __name__ == '__main__':
    pass