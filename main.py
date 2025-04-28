import cv2
import numpy as np
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMessageBox,QFileDialog
from PyQt6.QtCore import Qt, QTimer
from skimage.morphology import skeletonize
from superqt import QRangeSlider
import socket
rng = np.random.default_rng()
godot_host = "127.0.0.1"  # Godot server IP
godot_port = 5501         # Godot server port

w = 320
h = 240

def messageBox(title,msg,boxtype):
    # Create a message box
    msgBox = QMessageBox()
    msgBox.setIcon(boxtype)
    msgBox.setText(msg)
    msgBox.setWindowTitle(title)
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
    msgBox.exec()

class SliderWindow(QMainWindow):
    def __init__(self, camera_feed=None):
        # Initialize the main window
        super().__init__()
        self.camera_feed = camera_feed
        self.setWindowTitle("Hoolahoop Detector")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Initialize parameters
        self.ho = False
        self.h = [0,255]
        self.s = [0,255]
        self.v = [0,255]
        self.e = [13,50]
        self.c = [45,100]
        self.vis = True

        # Viewport for filtered camera feed
        self.camera_label = QLabel()
        self.layout.addWidget(self.camera_label)
        self.camera_label.setFixedSize(w,h)

        # Viewport for detected hoolahoop
        self.edges_label = QLabel()
        self.layout.addWidget(self.edges_label)
        self.edges_label.setFixedSize(w,h)

        # hue slider
        self.slider_hue_label = QLabel(f"Hue Range: {self.h[0]} - {self.h[1]}")
        self.layout.addWidget(self.slider_hue_label)
        self.slider_h = QRangeSlider(Qt.Orientation.Horizontal)
        self.slider_h.setMinimum(0)
        self.slider_h.setMaximum(255)
        self.slider_h.setValue(self.h)
        self.slider_h.valueChanged.connect(self.update_hue_range)
        self.layout.addWidget(self.slider_h)

        # saturation slider
        self.slider_saturation_label = QLabel(f"Saturation Range: {self.s[0]} - {self.s[1]}")
        self.layout.addWidget(self.slider_saturation_label)
        self.slider_s = QRangeSlider(Qt.Orientation.Horizontal)
        self.slider_s.setMinimum(0)
        self.slider_s.setMaximum(255)
        self.slider_s.setValue(self.s)
        self.slider_s.valueChanged.connect(self.update_saturation_range)
        self.layout.addWidget(self.slider_s)

        # value slider
        self.slider_value_label = QLabel(f"Value Range: {self.v[0]} - {self.v[1]}")
        self.layout.addWidget(self.slider_value_label)
        self.slider_v = QRangeSlider(Qt.Orientation.Horizontal)
        self.slider_v.setMinimum(0)
        self.slider_v.setMaximum(255)
        self.slider_v.setValue(self.v)
        self.slider_v.valueChanged.connect(self.update_value_range)
        self.layout.addWidget(self.slider_v)

        # parameter sliders for object detection preprocessing
        # gaussian blur radius
        self.slider_edge_r_label = QLabel(f"Edge Radius: {self.e[0]}")
        self.layout.addWidget(self.slider_edge_r_label)
        self.slider_edge_r = QSlider(Qt.Orientation.Horizontal)
        self.slider_edge_r.setMinimum(0)
        self.slider_edge_r.setMaximum(50)
        self.slider_edge_r.setValue(self.e[0])
        self.slider_edge_r.valueChanged.connect(self.update_edge_radius)
        self.layout.addWidget(self.slider_edge_r)
        # object threshold
        self.slider_edge_t_label = QLabel(f"Edge Threshold: {self.e[1]}")
        self.layout.addWidget(self.slider_edge_t_label)
        self.slider_edge_t = QSlider(Qt.Orientation.Horizontal)
        self.slider_edge_t.setMinimum(0)
        self.slider_edge_t.setMaximum(255)
        self.slider_edge_t.setValue(self.e[1])
        self.slider_edge_t.valueChanged.connect(self.update_edge_threshold)
        self.layout.addWidget(self.slider_edge_t)

        # camera fov
        self.slider_camera_fov_label = QLabel(f"Camera FOV: {self.c[0]}")
        self.layout.addWidget(self.slider_camera_fov_label)
        self.slider_camera_fov = QSlider(Qt.Orientation.Horizontal)
        self.slider_camera_fov.setMinimum(0)
        self.slider_camera_fov.setMaximum(180)
        self.slider_camera_fov.setValue(self.c[0])
        self.slider_camera_fov.valueChanged.connect(self.update_camera_fov)
        self.layout.addWidget(self.slider_camera_fov)

        # hoop diameter
        self.slider_hoop_diameter_label = QLabel(f"Hoop Diameter: {self.c[1]}")
        self.layout.addWidget(self.slider_hoop_diameter_label)
        self.slider_hoop_d = QSlider(Qt.Orientation.Horizontal)
        self.slider_hoop_d.setMinimum(0)
        self.slider_hoop_d.setMaximum(200)
        self.slider_hoop_d.setValue(self.c[1])
        self.slider_hoop_d.valueChanged.connect(self.update_hoop_diameter)
        self.layout.addWidget(self.slider_hoop_d)

        # Button to disable camera preview to increase performance
        button_layout = QHBoxLayout()
        self.visualize_button = QPushButton("Stop Visualization")
        self.visualize_button.clicked.connect(self.toggle_visualization)
        button_layout.addWidget(self.visualize_button)

        # Button to toggle Hue Out of range mode. Useful for red Objects
        self.hue_outside_button = QPushButton("Hue Out-Of Range Mode")
        self.hue_outside_button.clicked.connect(self.toggle_hue_outside)
        button_layout.addWidget(self.hue_outside_button)

        # Buttons to save and load parameters
        self.save_button = QPushButton("Save Parameters")
        self.save_button.clicked.connect(self.saveParameters)
        button_layout.addWidget(self.save_button)
        self.load_button = QPushButton("Load Parameters")
        self.load_button.clicked.connect(self.loadParameters)
        button_layout.addWidget(self.load_button)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        self.layout.addWidget(button_widget)

    # Toggle camera preview for performance
    def toggle_visualization(self):
        self.vis = not self.vis
        if self.vis:
            self.visualize_button.setText("Stop Visualization")
        else:
            self.visualize_button.setText("Start Visualization")
            self.camera_label.setText("Visualization disabled...")
            self.edges_label.clear()

    def toggle_hue_outside(self):
        self.ho = not self.ho
        if self.ho:
            self.hue_outside_button.setText("Hue In Range Mode")
        else:
            self.hue_outside_button.setText("Hue Out-Of Range Mode")

    # Update the ranges of the sliders
    def update_hue_range(self):
        self.h = self.slider_h.value()
        self.slider_hue_label.setText(f"Hue Range: {self.h[0]} - {self.h[1]}")

    def update_saturation_range(self):
        self.s = self.slider_s.value()
        self.slider_saturation_label.setText(f"Saturation Range: {self.s[0]} - {self.s[1]}")

    def update_value_range(self):
        self.v = self.slider_v.value()
        self.slider_value_label.setText(f"Value Range: {self.v[0]} - {self.v[1]}")

    def update_edge_radius(self):
        self.e[0] = self.slider_edge_r.value()
        self.slider_edge_r_label.setText(f"Edge Radius: {self.e[0]}")

    def update_edge_threshold(self):
        self.e[1] = self.slider_edge_t.value()
        self.slider_edge_t_label.setText(f"Edge Threshold: {self.e[1]}")

    def update_camera_fov(self):
        self.c[0] = self.slider_camera_fov.value()
        self.slider_camera_fov_label.setText(f"Camera FOV: {self.c[0]}")

    def update_hoop_diameter(self):
        self.c[1] = self.slider_hoop_d.value()
        self.slider_hoop_diameter_label.setText(f"Hoop Diameter: {self.c[1]}")

    # Save and parameters to file
    def saveParameters(self):
        with open("parameters.txt", "w") as f:
            f.write(f"{self.h[0]},{self.h[1]}\n")
            f.write(f"{self.s[0]},{self.s[1]}\n")
            f.write(f"{self.v[0]},{self.v[1]}\n")
            f.write(f"{self.e[0]},{self.e[1]}\n")
            f.write(f"{self.c[0]},{self.c[1]}\n")
            f.write(f"{self.ho}")
        messageBox("Parameters Saved", "Parameters saved successfully.", QMessageBox.Icon.Information)
    
    # Load parameters from file
    def loadParameters(self):
        try:
            with open("parameters.txt", "r") as f:
                lines = f.readlines()
                self.h = list(map(int, lines[0].strip().split(",")))
                self.s = list(map(int, lines[1].strip().split(",")))
                self.v = list(map(int, lines[2].strip().split(",")))
                self.e = list(map(int, lines[3].strip().split(",")))
                self.c = list(map(int, lines[4].strip().split(",")))
                self.ho = bool(lines[5].strip())
            messageBox("Parameters Loaded", "Parameters loaded successfully.", QMessageBox.Icon.Information)
        except FileNotFoundError:
            messageBox("Loading Failed", "No parameter-file found!", QMessageBox.Icon.Warning)
        except Exception as e:
            messageBox("Loading Failed", f"An error occurred while loading parameters: {e}", QMessageBox.Icon.Warning)
    
    # main function to update the camera feed and detect the hoolahoop
    def update_frame(self):
        # Read frame from camera
        ret, frame = self.camera_feed.read()
        if not ret:
            print("Error: Could not read frame.")
            return
        
        # hsv range keying
        if self.ho:
            gray1 = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), np.array((0,self.s[0],self.v[0])), np.array((self.h[0],self.s[1],self.v[1])))
            gray2 = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), np.array((self.h[1],self.s[0],self.v[0])), np.array((255,self.s[1],self.v[1])))
            gray = gray1+gray2
        else:
            gray = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), np.array((self.h[0],self.s[0],self.v[0])), np.array((self.h[1],self.s[1],self.v[1])))
        edge_r=self.e[0]*2+1
        # Apply Gaussian blur and thresholding to remove small-scale noise
        blurred = cv2.GaussianBlur(gray, (edge_r, edge_r), 0).astype(np.uint8)
        _, binary = cv2.threshold(blurred, self.e[1], 255, cv2.THRESH_BINARY)
        # convert to binary
        binary_bool = binary > 0  # convert to boolean mask
        # use skeletonize to find center line of the hoop
        skeleton = skeletonize(binary_bool)

        if self.vis:
            # If visualization is on, draw the skeleton on the original frame
            masked = cv2.bitwise_and(frame, frame, mask=gray)
            masked[skeleton] = (255,255,255)
            self.camera_label.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(masked.data, masked.shape[1], masked.shape[0], masked.strides[0], QtGui.QImage.Format.Format_BGR888)))

        # Find the coordinates of the skeleton points
        y_coords, x_coords = np.where(skeleton)
        coords = np.column_stack((x_coords, y_coords))
        #reshape to format expected by cv2.fitEllipse
        coords = coords.reshape((-1, 1, 2))
            
        #if enough points are found, fit an ellipse to the coordinates
        if len(coords) >= 5:
            frame_width = frame.shape[1]
            frame_height = frame.shape[0]
            ellipse = cv2.fitEllipse(coords)
            # Extract the parameters of the fitted ellipse
            pos = ellipse[0]
            size = ellipse[1][1]
            ratio = ellipse[1][0] / ellipse[1][1]
            angle = ellipse[2]

            # Calculate the distance of the hoop from the camera
            ang_size = (size/frame_width) * self.c[0]
            distance = self.c[1] / (2 * np.tan(np.radians(ang_size / 2)))

            # get ratio of visible hoop above and below major axis, to determine, which side of the hoop is facing the camera (the other side is occluded by human)
            above_line = 0
            below_line = 0
            for x, y in coords.reshape(-1, 2):
                if (x - pos[0]) * np.sin(np.radians(angle)) - (y - pos[1]) * np.cos(np.radians(angle)) > 0:
                    above_line += 1
                else:
                    below_line += 1
            if(above_line>below_line):
                tilt = -1
            else:
                tilt = 1

            # Calculate the pitch angle of the hoop
            pitch = np.degrees(np.arccos(ratio))*tilt

            # if visualization is on, display the detected hoop, major axis and normal on the camera frame
            if self.vis:
                end_x = int(pos[0] + (size / 2) * np.cos(np.radians(angle+90)))
                end_y = int(pos[1] + (size / 2) * np.sin(np.radians(angle+90)))
                start_x = int(pos[0] - (size / 2) * np.cos(np.radians(angle+90)))
                start_y = int(pos[1] - (size / 2) * np.sin(np.radians(angle+90)))
                #draw the major axis
                cv2.line(frame, (start_x, start_y), (end_x, end_y), (255, 0, 0), 2)

                # Calculate the normal direction vector
                normal_length = np.sin(np.radians(pitch))*10 # Adjust length based on distance for 3D appearance
                normal_x = int(pos[0] + normal_length * np.cos(np.radians(angle))*10)
                normal_y = int(pos[1] + normal_length * np.sin(np.radians(angle))*10)

                # Draw the normal direction line
                cv2.line(frame, (int(pos[0]), int(pos[1])), (normal_x, normal_y), (0, 0, 255), 2)

                #draw the ellipse
                cv2.ellipse(frame, ellipse, (0, 255, 0), 2)

            # Convert pos from pixel coordinates to angular diversion
            pos = np.array([pos[0] - frame_width/2, pos[1] - frame_height/2])
            angular_pos = pos * (2/frame_width) * self.c[0]
            # Calculate absolute x and y position based on angular position and distance
            absolute_x = distance * np.sin(np.radians(angular_pos[0]))
            absolute_y = distance * np.sin(np.radians(angular_pos[1]))

            # prepare message and yeet to udp receiver
            message = f"{absolute_x/100},{absolute_y/100},{distance/100},{angle},{pitch}"
            sock.sendto(message.encode(), (godot_host, godot_port))
        
        # if vizualization is on, display camera image
        if(self.vis):
            self.edges_label.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QtGui.QImage.Format.Format_BGR888)))
            
# get list of availeable cameras
def get_available_captures():
    available_captures = []
    for i in range(10):  # Check the first 10 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_captures.append(i)
            cap.release()
    return available_captures

# camera selection window
class CameraSelectionWindow(QMainWindow):
    def __init__(self,sources):
        super().__init__()
        self.setWindowTitle("Select Camera Source")
        self.setGeometry(100, 100, 300, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.label = QLabel("Select a camera source:")
        self.layout.addWidget(self.label)

        self.camera_buttons = []
        self.selected_camera = None

        available_captures = sources

        # for all availeable cameras, display a button to select camera
        for cam_index in available_captures:
            button = QPushButton(f"Camera {cam_index}")
            button.clicked.connect(self.select_camera(cam_index))
            self.layout.addWidget(button)
            self.camera_buttons.append(button)

    def select_camera(self, cam_index):
        def inner():
            self.selected_camera = cam_index
            self.close()
        return inner
    
# get availeable cameras
sources = get_available_captures()

app = QApplication([])

if len(sources) == 0:
    # if no availeable cameras, quit
    messageBox("No Camera Found", "No available camera sources were detected.", QMessageBox.Icon.Warning)
    exit()
elif len(sources) == 1: 
    # if one availeable camera, use that 
    cam = sources[0]
else:
    # else, let user choose
    camera_selection_window = CameraSelectionWindow()
    camera_selection_window.show()
    app.exec()

    cam = camera_selection_window.selected_camera

    if cam is None:
        print("No camera selected.")
        exit()

# open camera
cap = cv2.VideoCapture(cam)
# Set the resolution of the camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

# start main window
window = SliderWindow(cap)
window.show()
# create timer to update frame over and over again
timer = QTimer()
timer.timeout.connect(window.update_frame)
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        timer.start(0)
        app.exec()
except Exception as e:
    messageBox("Error", "An error occurred: " + str(e), QMessageBox.Icon.Warning)