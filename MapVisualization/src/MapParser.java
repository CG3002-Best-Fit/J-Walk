import org.json.*;

public class MapParser {
	
	private static LevelMap currentLevelMap;

	public static LevelMap parseJsonResult(String result) {
		JSONObject mainObject = new JSONObject(result);
		currentLevelMap = new LevelMap();
		try {
			JSONObject mapInfo = mainObject.getJSONObject("info");
			JSONArray nodeList = mainObject.getJSONArray("map");
			JSONArray wifiList = mainObject.getJSONArray("wifi");
			
			currentLevelMap.setNorthAt(mapInfo.getInt("northAt"));
			
			parseLOINodeJSON(nodeList);
			parseWifiNodeJSON(wifiList);
		} catch (JSONException e) {
			System.out.println("Loading Error!");
		}
		return currentLevelMap;
	}

	private static void parseWifiNodeJSON(JSONArray wifiList) {
		for(int i=0;i<wifiList.length();i++) {
			JSONObject node = wifiList.getJSONObject(i);
			int nodeId = node.getInt("nodeId");
			int x = node.getInt("x");
			int y = node.getInt("y");
			String nodeName = node.getString("nodeName");
			String macAddr = node.getString("macAddr");
			currentLevelMap.addWifiNode(new WifiNode(nodeId, x, y, nodeName,macAddr));
		}
	}

	private static void parseLOINodeJSON(JSONArray nodeList) {
		for(int i=0;i<nodeList.length();i++) {
			JSONObject node = nodeList.getJSONObject(i);
			int nodeId = node.getInt("nodeId");
			int x = node.getInt("x");
			int y = node.getInt("y");
			String nodeName = node.getString("nodeName");
			currentLevelMap.addLOINode(new LOINode(nodeId, x, y, nodeName));
		}
		
		for(int i=0;i<nodeList.length();i++) {
			JSONObject node = nodeList.getJSONObject(i);
			int nodeId = node.getInt("nodeId");
			String[] linkTo = node.getString("linkTo").split(",");
			
			for(int j=0;j<linkTo.length;j++) {
				int nextId = Integer.valueOf(linkTo[j].trim());
				currentLevelMap.connect(nodeId, nextId);
			}
		}
		
	}
}
