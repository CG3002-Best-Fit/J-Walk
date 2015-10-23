import java.awt.Color;
import java.awt.Graphics;
import java.awt.Point;
import java.awt.Polygon;
import java.util.ArrayList;

import javax.swing.JPanel;

public class MapPainterPanel extends JPanel {
	/**
	 * 
	 */
	private static final long serialVersionUID = 3223110041482748760L;
	private LevelMap currentLevelMap;
	private int offsetX = 0;
	private int offsetY = 0;
	private int oldX;
	private int oldY;
	private double zoomFactor;
	private boolean isNodeNameShown;
	private boolean isNodeIdShown;
	private int curX;
	private int curY;
	private double curDir;
	private static final int NODE_RADIUS = 5;
	
	public MapPainterPanel() {
		currentLevelMap = new LevelMap();
		offsetX = 10;
		offsetY = 10;
		zoomFactor = 0.1;
		curX = 0;
		curY = 0;
		curDir = 0;
	}
	
	public void paintComponent(Graphics g) {
		this.setBackground(Color.WHITE);
		drawPaths(g);
		drawLOINodes(g);
		drawWifiNodes(g);
		drawCurPosition(g);
		drawNorthIndicator(g);
	}

	private void drawNorthIndicator(Graphics g) {
		Point[] p = {
				new Point(0, -10),
				new Point(-5, 10),
				new Point(5, 10)
			};
			
			Polygon poly = new Polygon();
			for(int i=0;i<3;i++) {
				p[i] = rotatePoint(p[i], currentLevelMap.getNorthAt());
				//System.out.println("p[i] = (" + p[i].x + ", " + p[i].y + ")");
				poly.addPoint(30 + p[i].x, 30 + p[i].y);
				//System.out.println("" + i + ": " + (translateX(curX) + p[i].x) +","+ (translateY(curY) + p[i].y));
			}
			
			g.setColor(Color.RED);
			g.fillPolygon(poly);
	}

	private void drawCurPosition(Graphics g) {
		Point[] p = {
			new Point(0, -10),
			new Point(-5, 10),
			new Point(5, 10)
		};
		
		Polygon poly = new Polygon();
		for(int i=0;i<3;i++) {
			p[i] = rotatePoint(p[i], currentLevelMap.getNorthAt() + curDir);
			//System.out.println("p[i] = (" + p[i].x + ", " + p[i].y + ")");
			poly.addPoint(translateX(curX) + p[i].x, translateY(curY) + p[i].y);
			//System.out.println("" + i + ": " + (translateX(curX) + p[i].x) +","+ (translateY(curY) + p[i].y));
		}
		
		g.setColor(Color.GREEN);
		g.fillPolygon(poly);
	}
	
	private int translateX(int x) {
		return (int) (offsetX + x*zoomFactor);
	}
	
	private int translateY(int y) {
		return (int) (offsetY + (currentLevelMap.getMaxY() - y)*zoomFactor);
	}
	
	private Point rotatePoint(Point p, double theta) {
		if (p != null) {
			theta = theta/180*Math.PI;
			int x = (int) (p.x * Math.cos(theta) - p.y * Math.sin(theta));
			int y = (int) (p.x * Math.sin(theta) + p.y * Math.cos(theta));
			return new Point(x, y);
		}
		return null;
	}
	
	private void drawPaths(Graphics g) {
		ArrayList<LOINode> nodeList = currentLevelMap.getLOINodeList();
		
		for(int i=0;i<nodeList.size();i++) {
			LOINode node = nodeList.get(i);
			int fromX = translateX(node.getX());
			int fromY = translateY(node.getY());
			
			for(int j=0;j<node.getLinkTo().size();j++) {
				LOINode nextNode = node.getLinkTo().get(j);
				int toX = translateX(nextNode.getX());
				int toY = translateY(nextNode.getY());
				g.setColor(new Color(85,0,0));
				g.drawLine(fromX, fromY, toX, toY);
			}
		}
	}

	private void drawLOINodes(Graphics g) {
		ArrayList<LOINode> nodeList = currentLevelMap.getLOINodeList();
		
		for(int i=0;i<nodeList.size();i++) {
			LOINode node = nodeList.get(i);
			int x = translateX(node.getX());
			int y = translateY(node.getY());
			drawNode(g, x, y, new Color(255, 170, 170), new Color(85,0,0));
			if (isNodeNameShown) {
				g.drawString(node.getNodeName(), x + 1, y + 20);
			}
			if (isNodeIdShown) {
				g.drawString("" + node.getNodeId(), x - 15, y + 20);
			}
		}
	}
	
	private void drawWifiNodes(Graphics g) {
		ArrayList<WifiNode> nodeList = currentLevelMap.getWifiNodeList();
		
		for(int i=0;i<nodeList.size();i++) {
			WifiNode node = nodeList.get(i);
			int x = translateX(node.getX());
			int y = translateY(node.getY());
			drawNode(g, x, y, new Color(113, 142, 164), new Color(18, 54, 82));
			if (isNodeNameShown) {
				g.drawString(node.getNodeName(), x + 1, y - 10);
			}
			if (isNodeIdShown) {
				g.drawString("" + node.getNodeId(), x - 15, y - 10);
			}
		}
	}

	private void drawNode(Graphics g, int x, int y, Color mainColor, Color borderColor) {
		g.setColor(mainColor);
		g.fillOval(x - NODE_RADIUS, y - NODE_RADIUS, NODE_RADIUS*2, NODE_RADIUS*2);
		g.setColor(borderColor);
		g.drawOval(x - NODE_RADIUS, y - NODE_RADIUS, NODE_RADIUS*2, NODE_RADIUS*2);
	}

	public void drawMap(LevelMap currentLevelMap) {
		if (currentLevelMap != null) {
			this.currentLevelMap = currentLevelMap;
			this.repaint();
		}
	}

	public void increaseOffset(int x, int y) {
		offsetX += x - oldX;
		offsetY += y - oldY;
		oldX = x;
		oldY = y;
		repaint();
	}

	public void mousePressed(int x, int y) {
		oldX = x;
		oldY = y;
		
	}

	public void increaseZoomFactor(double d) {
		zoomFactor = Math.max(zoomFactor + d, 0);
		repaint();
	}

	public void showNodeName(boolean isNodeNameShown) {
		this.isNodeNameShown = isNodeNameShown;
		repaint();
	}

	public void showNodeId(boolean isNodeIdShown) {
		this.isNodeIdShown = isNodeIdShown;
		repaint();
	}

	public void setCurPosition(int x, int y, double dir) {
		curX = x;
		curY = y;
		curDir = dir;
		repaint();
	}
	
	public void setCurDir(double dir) {
		curDir = dir;
		repaint();
	}
}
