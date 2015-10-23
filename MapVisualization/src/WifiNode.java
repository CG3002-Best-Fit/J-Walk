
public class WifiNode extends Node {
	private String macAddr;
	
	public WifiNode(int nodeId, int x, int y, String nodeName, String macAddr) {
		super(nodeId, x, y, nodeName);
		this.macAddr = macAddr;
	}

	public String getMacAddr() {
		return macAddr;
	}

	public void setMacAddr(String macAddr) {
		this.macAddr = macAddr;
	}

}
