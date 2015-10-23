
public class Node {
	private int nodeId;
	private int x;
	private int y;
	private String nodeName;
	
	public Node(int nodeId, int x, int y, String nodeName) {
		this.setNodeId(nodeId);
		this.setX(x);
		this.setY(y);
		this.setNodeName(nodeName);
	}

	public int getNodeId() {
		return nodeId;
	}

	public void setNodeId(int nodeId) {
		this.nodeId = nodeId;
	}

	public int getX() {
		return x;
	}

	public void setX(int x) {
		this.x = x;
	}

	public int getY() {
		return y;
	}

	public void setY(int y) {
		this.y = y;
	}

	public String getNodeName() {
		return nodeName;
	}

	public void setNodeName(String nodeName) {
		this.nodeName = nodeName;
	}
}
