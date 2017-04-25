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
# image = cv.LoadImage('/Users/SamSong/Desktop/GUI/untitled/FirstBand/r0.25-h.k%02g.b%02g.z.teyodd-fixed.png' % (i,j))
image = cv.LoadImage('%s/sample002.png'%(FieldPath))
new = cv.CreateImage(cv.GetSize(image), image.depth, 1)
for imh in range(image.height):
    for imw in range(image.width):
        new[imh, imw] = (image[imh, imw][0]+image[imh, imw][1]+image[imh, imw][2])/3
cv.Threshold(new, new, 220, 255, cv.CV_THRESH_BINARY_INV)
sumx = []
# print sumx
for x in range(160):
    sum = 0
    for y in range(image.width):
        sum += new[x, y]
    if(sum == 0):
        sumx.append(x)

if(sumx<>[] and  min(sumx) > 90):
    print "Second Band"
else:
    print "Not Second Band"

print sumx

cv.ShowImage('a_window', new)
cv.WaitKey(0)
