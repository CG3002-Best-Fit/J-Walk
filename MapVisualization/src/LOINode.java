import java.util.ArrayList;


public class LOINode extends Node {
	private ArrayList<LOINode> linkTo = new ArrayList<LOINode>();
	
	public LOINode(int nodeId, int x, int y, String nodeName) {
		super(nodeId, x, y, nodeName);
	}

	public ArrayList<LOINode> getLinkTo() {
		return linkTo;
	}

	public void setLinkTo(ArrayList<LOINode> linkTo) {
		this.linkTo = linkTo;
	}
	
	public void addLinkTo(LOINode nextNode) {
		linkTo.add(nextNode);
	}
}
