import cv2.cv as cv
import csv
import numpy as np
import matplotlib.pyplot as plt
import subprocess
from PIL import Image
import numpy as np
import os


i = 01
j = 01
FieldPath='../DataFile/PNGlogfile'
# image = cv.LoadImage('%s/test_NoTaper/test_NoTaper_r0.3_mirror0.2/HO-nbm_2.83-wbm_1.5/0.2/Band%02g/r0.2-h.k%02g.b%02g.z.teyodd-fixed.png' % (FieldPath,j, i, j))
image = cv.LoadImage('%s/sample003.png'%(FieldPath))
new = cv.CreateImage(cv.GetSize(image), image.depth, 1)
for imh in range(image.height):
    for imw in range(image.width):
        new[imh, imw] = (image[imh, imw][0] + image[imh, imw]
                         [1] + image[imh, imw][2]) / 3
cv.Threshold(new, new, 220, 255, cv.CV_THRESH_BINARY_INV)
sumx = []
# print sumx
for x in range(100):
    sum = 0
    for y in range(image.width):
        sum += new[x, y]
    if(sum == 0):
        sumx.append(x)
if(sumx<>[] and max(sumx)<80 and min(sumx)>40):
    print "Third Band"
else:
    print "Not Third Band"
print sumx
cv.ShowImage('a_window', new)
cv.WaitKey(0)
