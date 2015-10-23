import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.EventQueue;

import javax.imageio.ImageIO;
import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;
import javax.swing.JScrollPane;

import java.awt.event.ItemListener;
import java.awt.event.ItemEvent;
import java.awt.event.MouseMotionAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseWheelListener;
import java.awt.event.MouseWheelEvent;

import javax.swing.JCheckBox;
import javax.swing.JTextField;

import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ConnectException;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;

import javax.swing.JLabel;

public class MapVisualization extends JFrame {

	/**
	 * 
	 */
	private static final long serialVersionUID = -7980495094965194879L;
	private JPanel contentPane;
	private LevelMap currentLevelMap;
	private MapPainterPanel mapPainterPanel;
	private JCheckBox showNodeNameCheckBox;
	private JCheckBox showNodeIdCheckBox;
	private JTextField currentPosTextField;
	private JTextField buildingLevelTextField;
	private JPanel imagePanel;
	private JLabel imageLabel;
	private JLabel numFrameLabel;
	private int numFrame;
	private JLabel curPosLabel;
	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					MapVisualization frame = new MapVisualization();
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the frame.
	 */
	public MapVisualization() {
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 1080, 600);
		
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		contentPane.setLayout(new BorderLayout(0, 0));

		initWidgets();
		
		SocketThread p = new SocketThread();
		p.start();
	}

	private void initWidgets() {
		initMapViewer();
		initTools();		
		initImageViewer();
		addListener();
		initDefaultValuesForTools();
		
		downloadSelectedMap();
		//receiveImage();
		
	}

	private void initDefaultValuesForTools() {
		// TODO Auto-generated method stub
		showNodeNameCheckBox.setSelected(true);
		showNodeIdCheckBox.setSelected(true);
		buildingLevelTextField.setColumns(10);
		currentPosTextField.setColumns(10);
		
	}

	private void addListener() {
		mapPainterPanel.addMouseWheelListener(new MouseWheelListener() {
			public void mouseWheelMoved(MouseWheelEvent e) {
				mapPainterPanel.increaseZoomFactor(-e.getWheelRotation() * 0.01);
			}
		});
		mapPainterPanel.addMouseListener(new MouseAdapter() {
			@Override
			public void mousePressed(MouseEvent e) {
				mapPainterPanel.mousePressed(e.getX(), e.getY());
			}
		});
		mapPainterPanel.addMouseMotionListener(new MouseMotionAdapter() {
			@Override
			public void mouseDragged(MouseEvent e) {
				mapPainterPanel.increaseOffset(e.getX(), e.getY());
			}
		});
		
		showNodeNameCheckBox.addItemListener(new ItemListener() {
			public void itemStateChanged(ItemEvent e) {
				if (e.getStateChange() == ItemEvent.SELECTED) {
					mapPainterPanel.showNodeName(true);
				} else {
					mapPainterPanel.showNodeName(false);
				}
			}
		});
		
		showNodeIdCheckBox.addItemListener(new ItemListener() {
			public void itemStateChanged(ItemEvent e) {
				if (e.getStateChange() == ItemEvent.SELECTED) {
					mapPainterPanel.showNodeId(true);
				} else {
					mapPainterPanel.showNodeId(false);
				}
			}
		});
		
		buildingLevelTextField.addKeyListener(new KeyAdapter() {
			@Override
			public void keyPressed(KeyEvent e) {
				if (e.getKeyCode() == KeyEvent.VK_ENTER) {
					downloadSelectedMap();
				}
			}
		});
		
		currentPosTextField.addKeyListener(new KeyAdapter() {
			@Override
			public void keyPressed(KeyEvent e) {
				if (e.getKeyCode() == KeyEvent.VK_ENTER) {
					String input = currentPosTextField.getText();
					if (input != null) {
						String[] inputValues = input.split(" ");
						if (inputValues.length >= 3) {
							int x = Integer.valueOf(inputValues[0]);
							int y = Integer.valueOf(inputValues[1]);
							double dir = Double.valueOf(inputValues[2]);
							//System.out.println("" + x + " " + y + " " + dir);
							
							mapPainterPanel.setCurPosition(x,y,dir);
						}
					}
				}
			}
		});
	}

	private void initImageViewer() {
		imagePanel = new JPanel();
		imagePanel.setBorder(new EmptyBorder(0, 10, 0, 0));
		imagePanel.setMinimumSize(new Dimension(640, 480));
		imagePanel.setPreferredSize(new Dimension(640, 480));
		contentPane.add(imagePanel, BorderLayout.EAST);
		
		imageLabel = new JLabel();
		imagePanel.add(imageLabel);
	}

	private void initMapViewer() {
		JScrollPane mapViewerScrollPane = new JScrollPane();
		mapPainterPanel = new MapPainterPanel();
		mapViewerScrollPane.setViewportView(mapPainterPanel);
		mapViewerScrollPane.setPreferredSize(new Dimension(640, 480));
		contentPane.add(mapViewerScrollPane, BorderLayout.CENTER);
	}

	private void initTools() {
		showNodeNameCheckBox = new JCheckBox("Node Name");
		showNodeIdCheckBox = new JCheckBox("Node Id");
		buildingLevelTextField = new JTextField();
		currentPosTextField = new JTextField();
		
		numFrame = 0;
		numFrameLabel = new JLabel("Frame: " + numFrame);
		curPosLabel = new JLabel("");
		
		JPanel toolPanel = new JPanel();
		toolPanel.add(buildingLevelTextField);
		toolPanel.add(showNodeIdCheckBox);
		toolPanel.add(showNodeNameCheckBox);
		toolPanel.add(currentPosTextField);
		toolPanel.add(numFrameLabel);
		toolPanel.add(curPosLabel);
		contentPane.add(toolPanel, BorderLayout.NORTH);
		
		
		
	}

	private void downloadSelectedMap() {
		if (buildingLevelTextField != null) {
			String[] input = buildingLevelTextField.getText().split(" ");
			if (input.length == 2) {
				String selectedBuilding = input[0];
				int selectedLevel = Integer.valueOf(input[1]);
				
				buildingLevelTextField.setEnabled(false);
				
				System.out.println("Downloading Map " + selectedBuilding + " " + selectedLevel);
				String result = MapDownloader.downloadMap(selectedBuilding, selectedLevel);
				
				buildingLevelTextField.setEnabled(true);
				
				if (!result.isEmpty()) {
					currentLevelMap = MapParser.parseJsonResult(result);
					mapPainterPanel.drawMap(currentLevelMap);
				}
			}
		}
	}
	
	/*private String byteToHex(byte b) {
		String map = "0123456789ABCDEF";
		String res = "";
		res += map.charAt((b&0xF0)>>4);
		res += map.charAt(b & 0x0F);
		return res;
	}*/
	
	
	class SocketThread extends Thread {
        //private static final String RPI_IP = "192.168.1.212";	// Sevin
        //private static final String RPI_IP = "192.168.0.109";	// Yushuen
		//private static final String RPI_IP = "172.25.103.50";	// COM1
		//private static final String RPI_IP = "192.168.2.3";		// Macbook
		private static final String RPI_IP = "192.168.43.212";		// Mobile
		
        //private static final String COM_IP = "192.168.1.107";
        
		private static final byte HELLO = 2;
        private static final byte ACK = 3;
		private static final byte POLL_REQUEST = 123;
		private OutputStream outputStream;
		private InputStream inputStream;
		private ServerSocket serverSocket;
		private boolean isPipeBroken;
		private boolean isACKed;
		private Socket clientSocket;
		private long lastTimeReceived;
		private byte[] imageBuf;
		private byte[] intBuf;
		SocketThread() {
			isPipeBroken = false;
			lastTimeReceived = 0;
			imageBuf = new byte[400000];
			intBuf = new byte[4];
        }

        public void run() {
        	try {
    			initSocket();
    			handShaking();
    			
    			while(!isPipeBroken) {
    				sendPollRequest();
    				readImage();
    				sleep(500);
    			}
    		} catch (IOException | InterruptedException e) {
    			e.printStackTrace();
    			
    		}
        }

		private void handShaking() throws IOException {
			do {
				sayHelloToRPi();
				waitingACK();
			} while ((!isACKed) && (!isPipeBroken));
		}

		private void initSocket() throws IOException, UnknownHostException {
			serverSocket = new ServerSocket(8001);
			System.out.println("Waiting for response...");
			Socket socket = serverSocket.accept();
			System.out.println("Accepted!");
			
			inputStream = socket.getInputStream();
			outputStream = null;
			do {
				System.out.println("Waiting for 1");
				int rcv = readInt();
				System.out.println(rcv);
				if (rcv == 1) {
					boolean isConnectToRPiSuccessful = false;
					while (!isConnectToRPiSuccessful) {
						try {
							clientSocket = new Socket(RPI_IP, 8003);
							outputStream = clientSocket.getOutputStream();
							isConnectToRPiSuccessful = true;
						} catch (ConnectException e) {
							isConnectToRPiSuccessful = false;
							System.out.println("Connection Failed!");
						}
					}
				}
			} while (outputStream == null);
		}
        
        private void waitingACK() throws IOException {
        	System.out.println("waiting for ACK");
			int rcv = readInt();
			System.out.println("rcv = " + rcv);
			isACKed = (rcv == ACK);
        	if (!isACKed) {
        		System.out.println("ACK failed!");
        	} else {
        		System.out.println("ACKed!");
        	}
		}

		private void sayHelloToRPi() {
			System.out.println("Saying Hello");
			sendInt(HELLO);
		}
        
        private void sendPollRequest() {
        	System.out.println("Send poll request");
        	sendInt(POLL_REQUEST);
		}
		
        
        private void sendInt(int u) {
        	intBuf[0] = (byte)((u & 0xFF000000)>>24);
        	intBuf[1] = (byte)((u & 0x00FF0000)>>16);
        	intBuf[2] = (byte)((u & 0x0000FF00)>>8);
        	intBuf[3] = (byte)((u & 0x000000FF));
        	try {
				outputStream.write(intBuf);
			} catch (IOException e) {
				e.printStackTrace();
				isPipeBroken = true;
			}
        }
        
		private int readInt() throws IOException {
        	inputStream.read(intBuf);
	        return ByteBuffer.wrap(intBuf).asIntBuffer().get();
        }
        
        private int readArr(byte[] buf, int size) throws IOException {
        	int bufSize = 0;
	        while(bufSize < size) {
	        	int readSize = inputStream.read(buf, bufSize, size);
		        //System.out.println("Read " + readSize + " bytes");
	        	if (readSize == -1) break;
		        bufSize += readSize;
	        }
	        return bufSize;
        }
        
		private void readImage() throws IOException {
			if (isPipeBroken) return;
			
			System.out.println("Reading: " + System.currentTimeMillis());
			int curBuilding = readInt();
			int curLevel = readInt();
			int curX = readInt();
			int curY = readInt();
			int heading = readInt();
			int sumStep = readInt();
			int ads = readInt();
			
			String temp = curBuilding + " " + curLevel;
			if ((buildingLevelTextField != null) && (!temp.equals(buildingLevelTextField.getText()))) {
				buildingLevelTextField.setText(temp);
				downloadSelectedMap();
			}
			
			System.out.println("X, Y, H = " + curX + ", " + curY + ", " + heading);
			//mapPainterPanel.set
			mapPainterPanel.setCurPosition(curX, curY, heading);
			numFrame++;
			curPosLabel.setText("Frame " + numFrame 
								+ "; (X, Y) = (" + curX + ", " + curY + "); " + heading + " deg; "
								+ "Sum of Steps: " + sumStep + "; ADS: " + ads);
			int size = readInt();
			System.out.println("Size = " + size);
			
			if (size > 0) {
				int readSize = readArr(imageBuf, size);
			    System.out.println("size = " + size + " readSize = " + readSize);
		        
			    if (size == readSize) {
		            
			        /*FileOutputStream fos = new FileOutputStream("image.jpg");
	        		fos.write(imageAr, 0, imageAr.length);
	        		fos.flush();
	        		fos.close();*/
			        
			        ByteArrayInputStream buffer = new ByteArrayInputStream(imageBuf, 0, size);
			        BufferedImage image = ImageIO.read(buffer);
			        
			        if (image != null) {
				        System.out.println("Received " + image.getHeight() + "x" + image.getWidth() + ": " + (System.currentTimeMillis()-lastTimeReceived) + " ms");
				        lastTimeReceived = System.currentTimeMillis();
				        imageLabel.setIcon(new ImageIcon(image));
				        numFrame++;
				        //double rate = numFrame/((System.currentTimeMillis() - startTime)/1000.0);
				        numFrameLabel.setText("Frame: " + numFrame );
				        
			        }
		        } else {
		        	System.out.println("Sending image failed!");
		        }
			}
	        
		}

		
    }
	
	
}
