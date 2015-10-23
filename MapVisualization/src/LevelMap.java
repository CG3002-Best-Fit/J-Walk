import java.util.ArrayList;
import java.util.HashMap;


public class LevelMap {
	private int northAt;
	private ArrayList<LOINode> LOINodeList = new ArrayList<LOINode>();
	private HashMap<Integer, LOINode> idToLOINodeMap = new HashMap<Integer, LOINode>();
	private ArrayList<WifiNode> WifiNodeList = new ArrayList<WifiNode>();
	private int maxX;
	private int maxY;
	
	public LevelMap() {
		LOINodeList = new ArrayList<LOINode>();
		idToLOINodeMap = new HashMap<Integer, LOINode>();
		WifiNodeList = new ArrayList<WifiNode>();
		maxX = 0;
		maxY = 0;
	}
	
	public int getNorthAt() {
		return northAt;
	}

	public void setNorthAt(int northAt) {
		this.northAt = northAt;
	}

	public ArrayList<LOINode> getLOINodeList() {
		return LOINodeList;
	}

	public void setLOINodeList(ArrayList<LOINode> lOINodeList) {
		LOINodeList = lOINodeList;
	}

	public ArrayList<WifiNode> getWifiNodeList() {
		return WifiNodeList;
	}

	public void setWifiNodeList(ArrayList<WifiNode> wifiNodeList) {
		WifiNodeList = wifiNodeList;
	}

	public void addLOINode(LOINode node) {
		idToLOINodeMap.put(node.getNodeId(), node);
		LOINodeList.add(node);
		maxX = Math.max(maxX, node.getX());
		maxY = Math.max(maxY, node.getY());
	}

	public void connect(int nodeAId, int nodeBId) {
		LOINode nodeA = idToLOINodeMap.get(nodeAId);
		LOINode nodeB = idToLOINodeMap.get(nodeBId);
		nodeA.addLinkTo(nodeB);
		nodeB.addLinkTo(nodeA);
	}

	public void addWifiNode(WifiNode wifiNode) {
		WifiNodeList.add(wifiNode);
		maxX = Math.max(maxX, wifiNode.getX());
		maxY = Math.max(maxY, wifiNode.getY());
	}

	public int getMaxX() {
		return maxX;
	}

	public int getMaxY() {
		return maxY;
	}

}
