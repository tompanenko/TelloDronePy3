# TelloSDKPy
DJI Tello drone python interface using the official [Tello SDK](https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf). 
Yes, this library has been tested with the drone. 
Please see [example.py](https://github.com/damiafuentes/TelloSDKPy/blob/master/example.py) for a working example controlling the drone as a remote controller with the keyboard and the video stream in a window.  

Tested with Python 3.6, but it also may be compatabile with other versions.

## Install
```
$ pip install djitellopy
```
or
```
$ git clone https://github.com/damiafuentes/TelloSDKPy.git
$ cd DJITelloPy
$ pip install requirements.txt
```

## Usage

### Simple example

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

### Example using pygame and the video stream
Please see [example.py](https://github.com/damiafuentes/TelloSDKPy/blob/master/example.py). 

The controls are:
- T: Takeoff
- L: Land
- Arrow keys: Forward, backward, left and right.
- A and D: Counter clockwise and clockwise rotations
- W and S: Up and down.

### Note
If you are using the ```streamon``` command and the response is ```Unknown command``` means you have to update the Tello firmware. That can be done through the Tello app.

### Installing OpenCV on Windows
1. Remove opencv from the anaconda install, if installed. "conda remove opencv" from Anaconda Prompt.
2. Download opencv 3.4.6 for windows from https://sourceforge.net/projects/opencvlibrary/files/3.4.6/opencv-3.4.6-vc14_vc15.exe/download
3. Run the opencv exe and unzipped the content to "<path to Tello>\Tello"
4. Then copy the file "<path to Tello>\Tello\opencv\build\python\cv2\python-2.7\cv2.pyd" to "<miniconda install path>\Miniconda2\Lib\site-packages" (note: on UBMS laptop, this path is C:\Users\ubound\AppData\Local\Continuum\miniconda2\Lib\site-packages)
5. Set a window Environment Variables as follows:
    1. OPENCV_DIR=<path to Tello>\opencv\build\x64\vc14
    2. Path=<previous stuff>;%OPENCV_DIR%\bin

Instructions adapted from: https://mathalope.co.uk/2015/05/07/opencv-python-how-to-install-opencv-python-package-to-anaconda-windows/

## Author

* **Damià Fuentes Escoté** 
* **Roberto Tron**
* **Bee Vang**

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/damiafuentes/TelloSDKPy/blob/master/LICENSE) file for details

