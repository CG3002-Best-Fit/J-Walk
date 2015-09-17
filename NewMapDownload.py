'''
Created on 12 Sep, 2015

@author: gaia_agito
'''
import urllib
import json

#This function serves to download the map and load it 
#Input= Block number and Level in char
#Output= All info downloaded from the weblink
def downloadMap(mapInfo):

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

def findShortestPath(mapInfo,startingID,startingBlock,startingFloor,endingID,endingBlock,endingFloor):
    distanceArray=[]
    distanceArray.append([])
    distanceArray[0].append(startingID)
    distanceArray[0].append(0)
    for eachMapInfo in mapInfo:
        if startingBlock== eachMapInfo[0] and startingFloor== eachMapInfo[1]:
            startingMap=eachMapInfo[3]
    for eachStartingMap in startingMap:
        if eachStartingMap['nodeId']== startingID:
            startingY= eachStartingMap['y']
            startingX= eachStartingMap['X']
            connectingID=[]
            for eachConnectingID in eachStartingMap['linkTo']:
                connectingID.append(eachConnectingID)
    
    print('haha')
    
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
    mapInfo =[]
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
        
    for x in xrange(0, maxRange):
        mapInfo.append([])
        mapInfo[x].append(buildingInfo[x][0])
        mapInfo[x].append(buildingInfo[x][1])
        mapInfo[x].append(totalInfoMatrix[x]['map'])

       
    print(mapInfo[1])
    print(mapInfo[1][2])
    
    #For checking purpose 
    #To be removed on later stage
    counter = 1

    for eachInfoMatrix in totalInfoMatrix:
        print (counter)
        print(eachInfoMatrix)
        counter = counter +1

if __name__ == "__main__":
    main()