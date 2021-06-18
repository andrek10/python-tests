from importlib import reload
import cv2
import numpy as np
from cv2 import aruco
from numba import njit
import matplotlib.pyplot as plt
import config
reload(config)
plt.close("all")

@njit(cache=True)
def maxpool(im_in, im_out):
    for i in range(0, im_out.shape[0]):
        for j in range(0, im_out.shape[1]):
            i1 = i*2
            i2 = i1 + 2
            j1 = j*2
            j2 = j1 + 2
            im_out[i, j] = np.max(im_in[i1:i2, j1:j2])

@njit(cache=True)
def average(im_in, im_out):
    for i in range(0, im_out.shape[0]):
        for j in range(0, im_out.shape[1]):
            i1 = i*2
            i2 = i1 + 2
            j1 = j*2
            j2 = j1 + 2
            im_out[i, j] = np.round(np.mean(im_in[i1:i2, j1:j2]))

def resize(im_in, s=1.0):
    im = np.array(im_in, copy=True)
    return cv2.resize(im, (int(s*im.shape[1]), int(s*im.shape[0])))

def get_color_image(im_in):
    im = np.zeros((im_in.shape[0], im_in.shape[1], 3), dtype=np.uint8)
    for i in range(0, 3):
        im[:, :, i] = np.array(im_in, copy=True)
    return im

class ArUcoDetectorOriginal:
    def __init__(self):
        # ArUco default parameters
        self.aruco_dict = aruco.Dictionary_get(getattr(aruco, "DICT_4X4_50"))
        self.aruco_parameters = aruco.DetectorParameters_create()

    def detect(self, image):
        corners, ids, rejectedImgPoints = aruco.detectMarkers(image, self.aruco_dict, parameters=self.aruco_parameters)
        return corners, ids, rejectedImgPoints

class ArUcoDetectorCustom:
    def __init__(self, algorithm_number):
        # ArUco default parameters
        self.aruco_dict = aruco.Dictionary_get(getattr(aruco, "DICT_4X4_50"))
        self.aruco_parameters = aruco.DetectorParameters_create()

        # Add Pixel refinement, as is useful for accurate pose estimation
        self.aruco_parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX

        # Set custom algorithm
        self.algorithm_number = algorithm_number
        if algorithm_number == 1: self.detect = self.custom1
        elif algorithm_number == 2: self.detect = self.custom2
        elif algorithm_number == 3: self.detect = self.custom3

    def custom1(self, image):
        """
        Set the adaptive threshold window step to 2 instead of 10
        """
        self.aruco_parameters.adaptiveThreshWinSizeStep = 2
        self.aruco_parameters.adaptiveThreshWinSizeMin = 7
        self.aruco_parameters.adaptiveThreshWinSizeMax = 7
        # self.aruco_parameters.minMarkerPerimeterRate = 0.02
        # self.aruco_parameters.polygonalApproxAccuracyRate = 0.05
        corners, ids, rejectedImgPoints = aruco.detectMarkers(image, self.aruco_dict, parameters=self.aruco_parameters)
        return corners, ids, rejectedImgPoints

    def custom2(self, image):
        """
        Iteratively test multiple adative threshold window steps.
        """
        for i in range(3, 100, 2):
            self.aruco_parameters.adaptiveThreshWinSizeStep = 2
            self.aruco_parameters.adaptiveThreshWinSizeMin = i
            self.aruco_parameters.adaptiveThreshWinSizeMax = i
            corners, ids, rejectedImgPoints = aruco.detectMarkers(image, self.aruco_dict, parameters=self.aruco_parameters)
            if ids is None:
                pass
            elif len(ids) > 0:
                print(f'Found Id {ids[0, 0]} on step {i}')
        return corners, ids, rejectedImgPoints

    def custom3(self, image):
        # Apply sharpening
        filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpen_image = cv2.filter2D(image, -1, filter)
        for i in range(3, 23+2, 2):
            self.aruco_parameters.adaptiveThreshWinSizeStep = i
            corners, ids, rejectedImgPoints = aruco.detectMarkers(sharpen_image, self.aruco_dict, parameters=self.aruco_parameters)
            if ids is None:
                pass
            elif len(ids) > 0:
                break
        return corners, ids, rejectedImgPoints

def adaptiveThreshold(im_in, block_size):
    src = np.array(im_in, copy=True)
    maxValue = 255  # What is assigned
    adaptiveMethod = cv2.ADAPTIVE_THRESH_MEAN_C
    thresholdType = cv2.THRESH_BINARY
    blockSize = block_size
    im = cv2.adaptiveThreshold(src, maxValue, adaptiveMethod, thresholdType, blockSize, 7)
    return im

def imshow(title, im):
    fig, ax = plt.subplots(figsize=(8,8))
    ax.imshow(im)
    ax.set_title(title)
    fig.tight_layout()

filename = config.filename
bool_maxpool = config.bool_maxpool
bool_average = config.bool_average

assert bool_average + bool_maxpool < 2

data_orig = cv2.imread(filename, cv2.IMREAD_ANYDEPTH)
if bool_maxpool:
    data = np.zeros((data_orig.shape[0]//2, data_orig.shape[1]//2))
    maxpool(data_orig, data)
    scale = 1.0
elif bool_average:
    data = np.zeros((data_orig.shape[0]//2, data_orig.shape[1]//2))
    average(data_orig, data)
    scale = 1.0
else:
    data = data_orig
    scale = 0.4
datamin = np.min(data)
datamax = np.max(data)

image = np.zeros_like(data, dtype=np.uint8)

image[:] = 255*((data - datamin) / (datamax - datamin))
image_copy = np.array(image, copy=True)
image_color = get_color_image(image)

aruco_detector = ArUcoDetectorOriginal()
corners, ids, rejectedImgPoints = aruco_detector.detect(image)
aruco.drawDetectedMarkers(image_color, corners, ids)
imshow(f'orignal', image_color)
image_color = get_color_image(image_copy)
aruco.drawDetectedMarkers(image_color, rejectedImgPoints)
imshow(f'orignal_rejected', image_color)

image = np.array(image_copy, copy=True)
image_color = get_color_image(image)

aruco_detector = ArUcoDetectorCustom(2)
corners, ids, rejectedImgPoints = aruco_detector.detect(image)
print('With custom found:')
print(ids)
aruco.drawDetectedMarkers(image_color, corners, ids)
imshow(f'custom', image_color)
image_color = get_color_image(image_copy)
aruco.drawDetectedMarkers(image_color, rejectedImgPoints)
imshow(f'custom_rejected', image_color)

image = np.array(image_copy, copy=True)
image_color = get_color_image(image)
image_thresh = adaptiveThreshold(image, 5)
imshow(f'threshold', image_thresh)

plt.show()