import cv2 as cv2
import numpy as np
import os
from PIL import Image
import math

########################################################################################################################

def stackImagesECC(file_list, r):
    M = np.eye(3, 3, dtype=np.float32)

    first_image = None
    stacked_image = None
    best_pixels = None
    best_sharpness = None

    for file in file_list:
        image = cv2.imread("focus/" + file, 1).astype(np.float32) / 255
        print(file)
        if first_image is None:
            first_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #first_image = image
            best_pixels = np.empty(image.shape)
            print(best_pixels.shape)
            best_sharpness = get_sharpness(best_pixels, r)
            stacked_image = image
        else:
            # Estimate perspective transform
            s, M = cv2.findTransformECC(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), first_image, M, cv2.MOTION_HOMOGRAPHY)
            w, h, _ = image.shape
            # Align image to first image
            image = cv2.warpPerspective(image, M, (h, w))

            sharpness = get_sharpness(image, r)
            better_indexes = np.where(sharpness > best_sharpness)

            best_pixels[better_indexes] = image[better_indexes]
            best_sharpness[better_indexes] = sharpness[better_indexes]

    #stacked_image = stacked_image / len(file_list)
    best_pixels = (best_pixels*255).astype(np.float32)

    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    #best_pixels = cv2.filter2D(best_pixels, -1, kernel)
    cv2.imwrite("merged.jpg", best_pixels)


#-----------------------------------------------------------------------------------------------------------------------

def get_sharpness(img, r):
    image = img.mean(axis = 2)
    blurred = cv2.GaussianBlur(image, (r, r), 0)
    sharp = np.abs(image - blurred)
    return sharp

########################################################################################################################

def crop_ROI(image):
    x, y, r = find_largest_circle(image)
    image = image.resize((614, 461), Image.ANTIALIAS)
    mask = np.zeros((461, 614, 3), dtype=np.uint8)
    cv2.circle(mask, (x, y), r, (255, 255, 255), -1, 2, 0)
    out = (image*mask) - 255
    white = mask - 255
    cv2.imwrite("test.jpg", white - out)

def crop_multiple(path):
    images = []
    for file in os.listdir(path):
        if os.path.isfile(path + "/" + file):
            images.append(path + "/" + file)
    for image_path in images:
        image = Image.open(image_path)
        x,y,r = find_largest_circle(image)
        if x == 0:
            continue
        image = image.resize((614, 461), Image.ANTIALIAS)
        mask = np.zeros((461, 614, 3), dtype=np.uint8)
        cv2.circle(mask, (x, y), r, (255, 255, 255), -1, 2, 0)
        out = (image*mask) - 255
        white = mask-255
        cv2.imwrite(image_path, white-out)




def find_largest_circle(image):
    image = image.resize((614, 461), Image.ANTIALIAS)
    image = np.array(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 100, param1=40, param2=74, minRadius=150, maxRadius=250)
    R = 0
    X = 0
    Y = 0

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for(x,y,r) in circles:
            R = r
            X = x
            Y = y

    #cv2.circle(output, (X,Y), R, (0,255,0), 4)
    #cv2.rectangle(output, (X-5,Y-5), (X+5,Y+5), (0,128,255))
    #cv2.imshow("output", np.hstack([output]))
    #cv2.waitKey(0)

    return X, Y, R


def find_center(image):
    image = np.array(image.convert("RGB"))
    h, w = image.shape[:2]
    x = w/2
    y = h/2
    return x, y

def laplacian_variance(image):
    image = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 12)
    return cv2.Laplacian(thresh, cv2.CV_64F).var()

def contrast_sum(image):
    #image = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 12)
    rows = gray.shape[0]
    cols = gray.shape[1]
    sum = 0
    for i in range(rows):
        for j in range(0, cols - 1, 1):
            sum += np.uint64(abs(gray[i,j] + gray[i,j+1]))
    return sum



