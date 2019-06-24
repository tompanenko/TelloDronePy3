﻿# TelloSDKPy
DJI Tello drone python interface using the official [Tello SDK](https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf). 
The package has been tested with Python 2.7 and 3.6 (macOS and Windows) and the drone connected using the default ad-hoc network, but it also may be compatible with other versions.

# Install
```
$ git clone https://tronroberto@bitbucket.org/tronroberto/pythondjitello.git DJITelloPy
$ cd DJITelloPy
$ pip install requirements.txt
```

# Usage

## Simple example

```
from djitellopy import Tello
import cv2
import time


tello = Tello()

tello.connect()

tello.takeoff()
time.sleep(5)

tello.move_left(100)
time.sleep(5)

tello.rotate_counter_clockwise(45)
time.sleep(5)

tello.land()
time.sleep(5)
        
tello.end()
```

## Examples
The following examples illustrate how to use different features of the package.
- test_path.py: Pre-programmed path motion
- test_mpads.py: Pre-programmed path motion using mission pads.
- test_state.py: Display the state broadcast by the drone.
- test_video.py: Display a live stream of the camera using 
- test_pygame.py: Keyboard teleoperation with live video streaming.

For test_pygame.py, the controls are:
- T: Takeoff
- L: Land
- Arrow keys: Forward, backward, left and right.
- A and D: Counter clockwise and clockwise rotations
- W and S: Up and down.
 


# Troubleshooting
## ```Unknown command``` response
If you are using the ```streamon``` command and the response is ```Unknown command``` means you have to update the Tello firmware. That can be done through the Tello app.

## Installing OpenCV on Windows
1. Remove opencv from the anaconda install, if installed. "conda remove opencv" from Anaconda Prompt.
2. Download opencv 3.4.6 for windows from https://sourceforge.net/projects/opencvlibrary/files/3.4.6/opencv-3.4.6-vc14_vc15.exe/download
3. Run the opencv exe and unzipped the content to "<path to Tello>\Tello"
4. Then copy the file "<path to Tello>\Tello\opencv\build\python\cv2\python-2.7\cv2.pyd" to "<miniconda install path>\Miniconda2\Lib\site-packages" (note: on UBMS laptop, this path is C:\Users\ubound\AppData\Local\Continuum\miniconda2\Lib\site-packages)
5. Set a window Environment Variables as follows:
    1. OPENCV_DIR=<path to Tello>\opencv\build\x64\vc14
    2. Path=<previous stuff>;%OPENCV_DIR%\bin

Instructions adapted from: https://mathalope.co.uk/2015/05/07/opencv-python-how-to-install-opencv-python-package-to-anaconda-windows/

# Tutorial handout
This package has been used as part of a 1-day workshop (around 6 hours) for the Boston University Upward Bound Math and Science program. This workshop was geared toward high-school students with no prior programming experience. Part of the workshop is based on the handout provided as LaTeX source under the tex directory.

# Known issues
Issuing the tello.stream_on() command quickly after the tello.takeoff() command sometimes results in the drone stopping to sending state updates and acknowledgements to commands for a few minutes (although the drone still might execute the commands).

# Original SDK documentation
The documentation for the SDK for the drone and the mission pads is available at https://www.ryzerobotics.com/tello-edu/downloads. A copy of the relevant PDF files is available under the `docs` subdirectory.

# Authors

* **Damià Fuentes Escoté** 
* **Roberto Tron**
* **Bee Vang**

# Credits

This repository is a fork of the original repository (https://github.com/damiafuentes/DJITelloPy) by Damià Fuentes Escoté. It includes several improvements, including: handling of the state sent by the drone, better management of sockets and timeouts, code for detecting faces using the classic OpenCV Haar Cascade, minor refactoring.


# License

This project is licensed under the MIT License - see the LICENSE.md file for details
