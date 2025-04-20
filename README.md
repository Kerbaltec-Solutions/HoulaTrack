# This is Houlatrack

![Preview Video](https://github.com/Kerbaltec-Solutions/HoulaTrack/blob/main/houlatrack.GIF)
*keep in mind, that this video was made under bad conditions, you can see position and rotation tracking working, however tilt direction aproximation does not work*

This python program is intedet to track a single houlahoop from a live camera capture. 

It publishes the spacial data via UDP to an expected server on 172.0.0.1:5501

Spacial data is provided as [x,y,z,tilt(left/right),pitch(foreward/backward)]

## Dependancies

* Python3
* A video capture source that is not used by another program
* The program is tested on Linux (Ubuntu) but should work on Windows as well

## Setup

1. After downloading the code from github, unpack the files and open the directory in the command line.

2. It is recommended to create a virtual enviroment 
   * `python3 -m venv venv`
   * `source venv/bin/activate`
3. Install neccessary python libraries
   * `pip install -r requirements.txt`

## Useage

0. If you used a venv for setup, you need to source it again.
   * `source venv/bin/activate`
1. Start the program
   * `python3 main.py`
2. You may be asked to select a camera source. Do so.
3. You should now see the main window. It is made up of the following items (top to bottom):
   1. Keyed image viewer (KIV)
      * Shows the input image after hsv-keying as well as the detected hoop-centerline.
   2. Hoop detection viewer (HDV)
      * Shows the detected houlahoop over the raw camera picture
   3. Value adjustment sliders
   4. Control Buttons

### Setup

4. The framerate might be very low right now, worry not, this will improve.
5. Adjust the hue, saturation and value sliders so, that the hoop is clearly vissible and uninterupted in the KIV. 
   * Raise the minimum and lower the maximum of each slider until the hoop starts to get filtered out
   * Then go over all values again to filter out background noise as good as possible without disrupting the hoop too much
6. Now adjust the values of the Edge-radius and Edge-threshold sliders, until there is a nice white line running along the center of the hoop and nowhere else in the KIV. 
   * You can also check, if the hoop is overlayed correctly on the HDV
   * If you cannot acive this reasonably well, you might need to change the color of your houlahoop. Make shure, that it is uniformly colored, matte and has a color that does not exist elsewhere in the surroundings.
7. To get accurate spacial information for the hoop, you now have to set the camera_fov slider to your cameras fov in degrees and the hoop diameter slider to the diameter of the houlahoop in *centimeters*
8. Click `Save parameters` to save the parameters for later

### Nominal useage

4. Click `Load parameters` to load the parameters from earlier
5. Data is now send via UDP. The program does not check, if data is received. 
   
### Data useage

* The *houlatrack-display* Godot project is a demo to show a virtual hoop being displaced based on the data
* Alternatively, you can run *server.py* to show the packages of data in the console
* Assuming camera pointing in -z direction:
   * For the position of the hoop, negate the x and z position values
   * For rotation of the hoop, first rotate around global x by the value of pitch, then rotate around global z by the value of tilt
* Absoloute adjustments to data (like adding 90°) might be neccessary

### Good to know

* Beware, that the program takes up the cammera you assingn to it. While the program is running, no other program will have access to that camera.
* Determining, which side of the hoop points towards the camera is tricky and highly dependant on a good hsv-keying of the hoop. While basic tracking might work in suboptimal conditions, Tilt-direction-detection might be more instable.
* It may be benificial to lower the cameras resolution to allow for higher framerate. This can be done by edinting lines 13 and 14 in the `main.py` file. The default should work well tho.
* In normal operation, you can disable the Preview windows by clicking `Stop Vizualization`. This frees up performance for higher framerate and other programs
* The program will work best with a matte, uniformly colored hoop, that does not share it's color with the surroundings and is not red.