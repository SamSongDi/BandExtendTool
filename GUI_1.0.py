# -*- coding: utf-8 -*-

#!/usr/bin/env python

from __future__ import unicode_literals
import sys
import os
# import random
from matplotlib.backends import qt_compat
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolBar

from matplotlib.figure import Figure
import matplotlib.pylab as plt

from pyqtgraph.dockarea import *

import pyqtgraph as pg
import pyqtgraph.console
import csv
import numpy as np

import subprocess
from PIL import Image
import numpy as np
import os
from matplotlib.patches import Polygon

app = QtGui.QApplication([])
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

import re

progname = os.path.basename(sys.argv[0])
progversion = "1.0"

# use to replace os.path.isfile()
import glob

####################################################################################################################################
###00005
def Canvas_onclick(event):
    """[summary]

    [description]Get the Coords on the Canvas

    Arguments:
        event {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    global ix, iy
    ix, iy = event.xdata, event.ydata
    print 'x = %f -> i = %d, y = %f' % (ix,ix/0.5*fig.Fulllength, iy)

    global coords
    coords = [ix, iy]

    return coords

def Text_Transform_Band1Fixed(s='[1,2],[3,4],[5,6]'):
    """[summary]
    
    [description]
    Use to transform the Text in form of '[x1,y1],[x2,y2]' to list 
    Keyword Arguments:
        s {str} -- [description] (default: {'[1,2],[3,4],[5,6]'})
    """
    global Band1Fixed
    f = re.findall(r'\d+', s)
    if(len(f)>1):
        k = [[int(f[0]), int(f[1])]]
        for i in range(len(f) / 2 - 1):
            k.append([int(f[2 * i + 2]), int(f[2 * i + 3])])
        Band1Fixed = k
    else:
        Band1Fixed=[]
def Text_Transform_Band2Fixed(s='[1,2],[3,4],[5,6]'):
    """[summary]
    
    [description]
    Use to transform the Text in form of '[x1,y1],[x2,y2]' to list 
    Keyword Arguments:
        s {str} -- [description] (default: {'[1,2],[3,4],[5,6]'})
    """
    global Band2Fixed
    f = re.findall(r'\d+', s)
    if(len(f)>1):
        k = [[int(f[0]), int(f[1])]]
        for i in range(len(f) / 2 - 1):
            k.append([int(f[2 * i + 2]), int(f[2 * i + 3])])
        Band2Fixed = k
    else:
        Band2Fixed=[]

def imagefilter1():
    global lines
    FilterBand1 = [[0 for col in range(BandNum)] for row in range(period)]
    for j in range(1, BandNum):
        for i in range(period):
            if(glob.glob('%s/FirstBand/Band%02g/*h.k%02g.b%02g*.png' % (fieldpath,j, i + 1, j))):
                FilterBand1[i][j] = 1
            else:
                print "k,band", i + 1, j
    print 'FilterBand1', FilterBand1
    for i in range(period):
        for j in range(1, BandNum):
            lines[i][j] = float(lines[i][j]) * float(FilterBand1[i][j])
            print "lines lines i,j",i ,j

def imagefilter2():
    FilterBand2 = [[0 for col in range(BandNum)] for row in range(period)]
    for j in range(1, BandNum):
        for i in range(period):
            if(glob.glob('%s/SecondBand/Band%02g/*h.k%02g.b%02g*.png' % (fieldpath,j, i + 1, j))):
                FilterBand2[i][j] = 1
            else:
                print "k,band", i + 1, j
    print 'FilterBand2', FilterBand2
    for i in range(period):
        for j in range(1, BandNum):
            lines[i][j] = float(lines[i][j]) * float(FilterBand2[i][j])

def Data_Export():
    fp = open("%s/Data.txt"%(fieldpath),'w')
    fp.write("i")
    fp.write(",")
    fp.write("Band1")
    fp.write(",")
    fp.write("k")
    fp.write(",")
    fp.write("band#")
    fp.write("\n")
    for i in range(len(Band1)):
        fp.write(str(i))
        fp.write(",")
        fp.write(str(Band2[i]))
        fp.write(",")
        fp.write(str(track1Band1[i][0]+1))
        fp.write(",")
        fp.write(str(track1Band1[i][1]))
        fp.write("\n")
    fp.write("\n")
    fp.write("i")
    fp.write(",")
    fp.write("Band2")
    fp.write(",")
    fp.write("k")
    fp.write(",")
    fp.write("band#")
    fp.write("\n")
    for i in range(len(Band2)):
        fp.write(str(i))
        fp.write(",")
        fp.write(str(Band2[i]))
        fp.write(",")
        fp.write(str(track1Band2[i][0]+1))
        fp.write(",")
        fp.write(str(track1Band2[i][1]))
        fp.write("\n")
    fp.close()

startband1=1
Band1Fixed=[]
startband2=16
Band2Fixed=[]
# Band2Fixed=[[510-34*3,99],[511-34*3,99],[527-34*3,99],[528-34*3,99],[535-34*3,96],[536-34*3,96]]

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # fig = Figure(figsize=(width, height), dpi=dpi)
        global fig1
        fig1 = plt.figure()
        plt.style.use('ggplot')
        self.axes = fig1.add_subplot(111)
        fig1.subplots_adjust(bottom=0.2,right=0.65)

        # We want the axes cleared every time plot() is called
        # self.axes.hold(False)


        # self.compute_initial_figure()
        # self.f1Plot()

        #
        FigureCanvas.__init__(self, fig1)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

    def DisplaySwitch_Init(self):
        global Display_Ref1
        global Display_Ref2
        global Display_Ref3
        global Display_Ref4
        global Display_Band1
        global Display_Band2
        global Display_Cavity
        global Display_Pcross
        global Display_Subplot
        global mkBand1PNG
        global mkBand2PNG
        global Display_Boundary
        global Display_Legend
        global Display_Derivative
        global csvpath
        global fieldpath
        global NHole
        global BandNum
        global startpoint1_b
        global startpoint1_k
        global startpoint2_b
        global startpoint2_k
        global Ref2
        global Ref4
        global Ref1
        global Ref3
        global legend_Ref1
        global legend_Ref2
        global legend_Ref3
        global legend_Ref4
        global Switch_Filter1
        global Switch_Filter2
        global End_Band
        global Start_Band
        global track2Band1
        global track2Band2
        global period
        global Display_lightcorn

        Display_Ref1 = 1
        Display_Ref2 = 1
        Display_Ref3 = 1
        Display_Ref4 = 1

        Display_Band1 = 1
        Display_Band2 = 1

        Display_Cavity = 0

        Display_Pcross = 0

        Display_Subplot = 1

        mkBand1PNG = 0
        mkBand2PNG = 0

        Display_Boundary = 1
        Display_Legend = 1
        Display_lightcorn=1

        Display_Derivative = 1

        csvpath = './DataFile/Hole40-r0.1.csv'
        fieldpath='./DataFile/PNGlogfile'
        # fieldpath='/Users/SamSong/Desktop/GUI/untitled'
        NHole = 40
        BandNum = 100
        period=34

        startpoint1_k=18
        startpoint1_b=1
        startpoint2_k=18
        startpoint2_b=16

        legend_Ref1='Reference First Band RROD=0.10'
        Ref1 = [0.0, 0.0251504, 0.0494593, 0.0717521, 0.0905083, 0.10496, 0.116102, 0.125494,
             0.134148, 0.14256, 0.150954, 0.159428, 0.168017, 0.176729, 0.185545, 0.194412, 0.203102, 0.208988]
        legend_Ref2='Reference First Band RROD=0.25'
        Ref2 = [0, 0.0252969, 0.0498416, 0.0726113, 0.092289, 0.108107, 0.120791, 0.131716, 0.141846,0.151657, 0.161344, 0.170954, 0.180446, 0.189696, 0.198452, 0.206208, 0.211974, 0.214207]
        legend_Ref3='Reference Second Band RROD=0.10'
        Ref3 = [0.123531, 0.124829, 0.128955, 0.136677, 0.149202, 0.167024, 0.18889, 0.212974,
             0.237945, 0.262836, 0.280369, 0.27083, 0.261153, 0.251537, 0.242014, 0.232643, 0.223651, 0.217664]
        legend_Ref4='Reference Second Band RROD=0.25'
        Ref4 = [0.124544, 0.125952, 0.130361, 0.138381, 0.150985, 0.168626, 0.190284, 0.214288,
                     0.239337, 0.264467, 0.288292, 0.301733, 0.295688, 0.286956, 0.278316, 0.270572, 0.264797, 0.262559]
        Switch_Filter1=0
        Switch_Filter2=0

        Start_Band=55
        End_Band=62

    def Band1FixedProcess(self,index=-1):
        i = index
        global track1Band1
        global track2Band1
        for k in range(len(Band1Fixed)):
            if(i == Band1Fixed[k][0]):
                Band1[i] = float(Band1lines[(i + 17) % period][Band1Fixed[k][1]])
                Pcross[i] = Band1[i]
                track1Band1[i] = [(i + 17) % period, Band1Fixed[k][1]]
                track2Band1[(i + 17) % period][Band1Fixed[k][1]] = 1
    def Band2FixedProcess(self,index=-1):
        i = index
        global track1Band2
        global track2Band2
        for k in range(len(Band2Fixed)):
            if(i == Band2Fixed[k][0]):
                Band2[i] = float(Band2lines[(i + 17) % period][Band2Fixed[k][1]])
                Pcross[i] = Band2[i]
                track1Band2[i] = [(i + 17) % period, Band2Fixed[k][1]]
                track2Band2[(i + 17) % period][Band2Fixed[k][1]] = 1

    def Band1Data(self, startband=1):
        #000051
        #Smoothness Fiter
        global Band1
        global track1Band1
        global track2Band1
        global period
        global Pcross
        self.startband1 = startband
        # fig, (ax11, ax2) = plt.subplots(2, 1)
        # ax12 = ax11.twinx()
        # NHole = 41
        OddFlag = '-Odd'
        FileName = csvpath
        csvfile = file(FileName, 'rb')
        Nk = period+1
        self.Nk=Nk

        Fulllength = period / 2 * NHole + 1
        self.Fulllength=Fulllength

        reader = csv.reader(csvfile)
        global lines
        lines = [line for line in reader]
        global Band1lines
        Band1lines=lines
        # Band1lines=[line for line in reader]
        print '!!!!!!!',Band1lines
        # print lines[17][1]
        # print linescopy[17][1]
        csvfile.close()

        # ####Adding Point
        inserttime = 0

        # csvfile = file('Hole%d%s.csv' % (NHole, OddFlag), 'rb')
        csvfile = file(FileName, 'rb')
        reader = csv.reader(csvfile)

        linescopy = [line for line in reader]
        # print lines[17][1]
        # print linescopy[17][1]
        csvfile.close()

        # #### FilterBand1
        if(Switch_Filter1):
            imagefilter1()

        # ####Adding Point
        inserttime = 0

        Band1 = range(Fulllength)
        for i in range(len(Band1)):
            Band1[i] = 0

        # Tracking Point two
        track2Band1 = [[0 for col in range(BandNum)] for row in range(period)]

        # testing
        Pcross = range(Fulllength)
        for i in range(len(Pcross)):
            Pcross[i] = 0

        y = range(period)
        maxy = 10
        gap = 0
        gaphistory = range(BandNum + inserttime)

        # Record Track of the index to recover the history of gap compressing
        track1Band1 = range(Fulllength+1)
        # mark1
        # startband = 1
        track1Band1[0] = [startpoint1_k-1, startpoint1_b]
        track1Band1[1] = [startpoint1_k, startpoint1_b]

        Band1[0] = float(lines[startpoint1_k-1][startpoint1_b])
        Band1[1] = float(lines[startpoint1_k][startpoint1_b])
        # get data which match the band1 dispersion line

        flag = 0
        buoy = 1
        j = 1
        d2mink = 1
        CrspdK = range(1, 35)

        # test
        life = 10

        for i in range(2, len(Band1)):
            flag = 1
            # d1 = float(lines[(i + 17) % period][1]) - Band1[i - 1]
            dmin = 1
            d2min = 1
            for k in range(1, len(lines[0])):
                if(k != len(lines[0])):
                    # if(float(lines[(i + 17) % period][j + 1]) == float(lines[(i + 17) % period][j])):
                        # Pcross[i] = Band1[i]
                    d0 = Band1[i - 1] - Band1[i - 2]
                    d2 = float(lines[(i + 17) % period][k]) - Band1[i - 1]
                    if(abs(d2 - d0) < abs(dmin - d0)):
                        Band1[i] = float(lines[(i + 17) % period][k])
                        track1Band1[i] = [(i + 17) % period, k]
                        dmin = d2
                        j = k
                        # if(i == 579):
                        # Band1[i] = float(lines[(i + 17) % period][k+2])
            for k in range(1, len(lines[0])):
                if(k != len(lines[0]) - 1):
                    # if(float(lines[(i + 17) % period][j + 1]) == float(lines[(i + 17) % period][j])):
                        # Pcross[i] = Band1[i]
                    d0 = Band1[i - 1] - Band1[i - 2]
                    d2 = float(lines[(i + 17) % period][k]) - Band1[i - 1]
                    if(abs(d2 - d0) <= abs(d2min - d0) and d2 != dmin):
                        d2min = d2
                        d2mink = k
                        # if(Band1[i] == Band1[i - 2]):
                        # print d2min
                        # Band1[i] = float(lines[(i + 17) % period][k])

            if(Band1[i] == Band1[i - 2] and ((i + 17) % period == 18 or (i + 17) % period == 1)):
                Pcross[i] = Band1[i]
                # print dmin, d2min
                life -= 1
                track1Band1[i] = [(i + 17) % period, d2mink]
                Band1[i] = float(lines[(i + 17) % period][d2mink])
            self.Band1FixedProcess(index=i)

            # if(i == 596 and self.startband == 1):
            #     Band1[i] = float(lines[(i + 17) % period][j + 1])
            #     # Pcross[i] = Band1[i]
            #     track1Band1[i] = [(i + 17) % period, j + 1]
            track2Band1[(i + 17) % period][track1Band1[i][1]] = 1
            print 'Band1', i, track1Band1[i], CrspdK[(i + 17) % period], Band1[i]

        x = range(len(Band1))
        x = [float(x[i]) / ((len(x) - 1) * 2) for i in range(len(x))]
        # plt.plot(x, Band1, '--')

        for i in range(Fulllength):
            Band1[i] = float(linescopy[int(track1Band1[i][0])][int(track1Band1[i][1])])
            # print i, track1Band1[i], Band1[i]
            if(Pcross[i] != 0):
                print '!!!'
            # x=range(16)
        # if(Display_Band1):
            # ax11.plot(x, Band1, '*', label='First Band')

        # if(Display_Band1 and Display_Derivative):
        #     dBand1 = [0 for i in range(Fulllength)]
        #     for i in range(Fulllength - 1):
        #         dBand1[i] = (Band1[i + 1] - Band1[i]) / (x[1] - x[0])
        #         print "dBand1", i, dBand1[i]
        #         if(i % 17 == 0 or i % 17 == 16):
        #             dBand1[i] = -10
        #     ax12.plot(x, dBand1, '+')
        #     ax12.axis([min(x), max(x), -0.5, 1])
        #     ax12.set_ylabel('$\partial v_D /\partial k$')

        # plt.plot([0, Fulllength - 1], [0, 1])
        print max(Band1)
        self.Band1 = Band1
        self.track1Band1 = track1Band1
        self.track2Band1 = track2Band1

        # if(Display_Pcross):
        #     ax11.plot(x, Pcross)
        #     for i in range(Fulllength):
        #         if(Pcross[i] != 0):
        #             print "Pcross:i", i
    def Band2Data(self,startband=16):
       #000051
       #Smoothness Fiter
        global Band2
        global track1Band2
        global track2Band2
        global period
        global Pcross
        self.startBand2 = startband
        # fig, (ax11, ax2) = plt.subplots(2, 1)
        # ax12 = ax11.twinx()    
        # NHole = 41
        OddFlag = '-Odd'
        FileName = csvpath

        csvfile = file(FileName, 'rb')
        Nk = period+1
        self.Nk=Nk

        Fulllength = period / 2 * NHole + 1
        self.Fulllength=Fulllength

        reader = csv.reader(csvfile)
        global lines
        lines = [line for line in reader]
        global Band2lines
        Band2lines=lines
        # Band2lines=[line for line in reader]
        print '!!!!!!!',Band2lines
        # print lines[17][1]
        # print linescopy[17][1]
        csvfile.close()

        # ####Adding Point
        inserttime = 0

        # csvfile = file('Hole%d%s.csv' % (NHole, OddFlag), 'rb')
        csvfile = file(FileName, 'rb')
        reader = csv.reader(csvfile)

        linescopy = [line for line in reader]
        # print lines[17][1]
        # print linescopy[17][1]
        csvfile.close()
        # y = range(period)
        # maxy = 10
        # gap = 0
        # gaphistory = range(BandNum + inserttime)

        # for i in range(1, BandNum):
        #     for j in range(period):
        #         y[j] = float(lines[j][i])
        #     if(min(y) > maxy):
        #         gap += min(y) - maxy
        #     else:
        #         gap += 0
        #     maxy = max(y)
        #     gaphistory[i] = gap
        #     for j in range(period):
        #         lines[j][i] = float(float(lines[j][i]) - gap)
        # #### FilterBand2
        if(Switch_Filter2):
            imagefilter2()
        # ####Adding Point
        inserttime = 0

        Band2 = range(Fulllength)
        for i in range(len(Band2)):
            Band2[i] = 0

        # Tracking Point two
        track2Band2 = [[0 for col in range(BandNum)] for row in range(period)]

        # testing
        Pcross = range(Fulllength)
        for i in range(len(Pcross)):
            Pcross[i] = 0

        y = range(period)
        maxy = 10
        gap = 0
        gaphistory = range(BandNum + inserttime)

        # Record Track of the index to recover the history of gap compressing
        track1Band2 = range(Fulllength+1)
        # mark1
        # startband = 1
        track1Band2[0] = [startpoint2_k-1, startpoint2_b]
        track1Band2[1] = [startpoint2_k, startpoint2_b]

        Band2[0] = float(lines[startpoint2_k-1][startpoint2_b])
        Band2[1] = float(lines[startpoint2_k][startpoint2_b])
        # get data which match the Band2 dispersion line

        flag = 0
        buoy = 1
        j = 1
        d2mink = 1
        CrspdK = range(1, 35)

        # test
        life = 15

        for i in range(2, len(Band2)):
            flag = 1
            # d1 = float(lines[(i + 17) % period][1]) - Band2[i - 1]
            dmin = 1
            d2min = 1
            for k in range(1, len(lines[0])):
                if(k != len(lines[0])):
                    # if(float(lines[(i + 17) % period][j + 1]) == float(lines[(i + 17) % period][j])):
                        # Pcross[i] = Band2[i]
                    d0 = Band2[i - 1] - Band2[i - 2]
                    d2 = float(lines[(i + 17) % period][k]) - Band2[i - 1]
                    if(abs(d2 - d0) < abs(dmin - d0)):
                        Band2[i] = float(lines[(i + 17) % period][k])
                        track1Band2[i] = [(i + 17) % period, k]
                        dmin = d2
                        j = k
                        # if(i == 579):
                        # Band2[i] = float(lines[(i + 17) % period][k+2])
            for k in range(1, len(lines[0])):
                if(k != len(lines[0]) - 1):
                    # if(float(lines[(i + 17) % period][j + 1]) == float(lines[(i + 17) % period][j])):
                        # Pcross[i] = Band2[i]
                    d0 = Band2[i - 1] - Band2[i - 2]
                    d2 = float(lines[(i + 17) % period][k]) - Band2[i - 1]
                    if(abs(d2 - d0) <= abs(d2min - d0) and d2 != dmin):
                        d2min = d2
                        d2mink = k
                        # if(Band2[i] == Band2[i - 2]):
                        # print d2min
                        # Band2[i] = float(lines[(i + 17) % period][k])
            # if(Band2[i] == Band2[i - 2] and life > 0 and ((i + 17) % period == 18 or (i + 17) % period == 1)):
            if(Band2[i] == Band2[i - 2] and ((i + 17) % period == 18 or (i + 17) % period == 1)):

                Pcross[i] = Band2[i]
                # print dmin, d2min
                life -= 1
                track1Band2[i] = [(i + 17) % period, d2mink]
                track2Band2[(i + 17) % period][d2mink] = 1
                track1Band2[i - 1] = [(i + 17 - 1) % period, d2mink]
                track2Band2[(i + 17 - 1) % period][d2mink] = 1
                Band2[i] = float(lines[(i + 17) % period][d2mink])
                Band2[i - 1] = float(lines[(i + 17 - 1) % period][d2mink])

            self.Band2FixedProcess(index=i)

            track2Band2[(i + 17) % period][track1Band2[i][1]] = 1
            print 'Band2', i, track1Band2[i], CrspdK[(i + 17) % period], Band2[i]

        x = range(len(Band2))
        x = [float(x[i]) / ((len(x) - 1) * 2) for i in range(len(x))]
        # plt.plot(x, Band2, '--')

        for i in range(Fulllength):
            Band2[i] = float(linescopy[int(track1Band2[i][0])][int(track1Band2[i][1])])
            # print i, track1Band2[i], Band2[i]
            if(Pcross[i] != 0):
                print '!!!'
            # x=range(16)
        # if(Display_Band2):
        #     ax11.plot(x, Band2, '*', label='Second Band')

        # if(Display_Band2 and Display_Derivative):
        #     dBand2 = [0 for i in range(Fulllength)]
        #     for i in range(Fulllength - 1):
        #         dBand2[i] = (Band2[i + 1] - Band2[i]) / (x[1] - x[0])
        #         print "dBand2", i, dBand2[i]
        #         if(i % 17 == 0 or i % 17 == 16):
        #             dBand2[i] = -10
        #     ax12.plot(x, dBand2, '+')
        #     ax12.axis([min(x), max(x), -0.5, 1])
        #     ax12.set_ylabel('$\partial v_D /\partial k$')

        # plt.plot([0, Fulllength - 1], [0, 1])
        print max(Band2)
        self.Band2 = Band2
        self.track1Band2 = track1Band2
        self.track2Band2 = track2Band2

        # if(Display_Pcross):
        #     ax11.plot(x, Pcross)
        #     for i in range(Fulllength):
        #         if(Pcross[i] != 0):
        #             print "Pcross:i", i



class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)



    def compute_initial_figure(self, x=[0, 1], y=[0, 1]):
        # x=np.arange(0,0.5+0.5/(len(Band1)-1),0.5/(len(Band1)-1))
        # y=Band1
        self.axes.plot(x, y)
    def Clear_Figure():
        # self.axes.hold(False)
        # self.draw(x=[0],y=[0],',')
        # self.axes.hold(True)
        pass
    def f1Plot(self, x=[0,1], y=[0,2]):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self.axes.plot(x, y, 'o',markersize=1.0, label='First Band')
        self.axes.set_xlabel('k/(2$\pi$/a)')
        self.axes.set_ylabel('$v_D$/(2$\pi$c/a)')

        self.draw()
    def f2Plot(self, x=[0,1], y=[0,2]):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self.axes.plot(x, y,'o',markersize=1.0, label='Second Band')
        # self.axes.plot(x, y, ',', label='Second Band')
        self.axes.set_xlabel('k/(2$\pi$/a)')
        self.axes.set_ylabel('$v_D$/(2$\pi$c/a)')
        self.draw()
    def fxPlot(self,x=[0,1],y=[0,2],l='fxPlot',s='o'):
        self.axes.plot(x,y,s,label=l)
        self.axes.set_xlabel('k/(2$\pi$/a)')
        self.axes.set_ylabel('$v_D$/(2$\pi$c/a)')
        self.draw()
    def plot_Boundary(self):
        xdash = [0.5*i/(NHole) for i in range(NHole+1)]
        markerline, stemlines, baseline = self.axes.stem(xdash, [1.5 for i in range(len(xdash))], 'k--')
        self.axes.axis([0,0.5,0,max(Band2)*1.25])
        self.draw()
    def plot_lightcorn(self):
        x = [0, 0.5]
        y = [0, 0.5]
        self.axes.plot(x, y, 'r')
        verts = [(0, 0)] + [(0, 0.5)] + [(0.5, 0.5)]
        poly = Polygon(verts, alpha=0.1, facecolor='r', edgecolor='r')
        self.axes.add_patch(poly)
        self.draw()
    def OverlapBand(self, start_band=55,end_band=62):
        FileName = csvpath
        csvfile = file(FileName, 'rb')
        reader = csv.reader(csvfile)
        lines = [line for line in reader]
        csvfile.close()

        # x = [-0.5+float(i)/(period) for i in range(period)]
        x = [float(i)/(period) for i in range(period/2+1)]
        # x = [(x[i] - float(max(x) / 2) - 1) / (len(x) - 1) for i in range(len(x))]

        y = range(period/2+1)
        band1y = range(period/2+1)
        band2y = range(period/2+1)
        maxy = 10
        gap = 0
        gaphistory = range(BandNum)

        for i in range(1, BandNum):
            for j in range(period):
                lines[j][i] = float(lines[j][i])

        StartBand = start_band
        EndBand = end_band
        for i in range(StartBand, EndBand + 1):
            for j in range(period/2+1):
                y[period/2-j] = float(lines[j][i])
            if(i == StartBand):
                miny = min(y)
            self.axes.plot(x, y, 'o', label=' %02g' % i,alpha=0.5)
            if(Display_Band1):
                for j in range(period/2+1):
                    band1y[period/2-j] = track2Band1[j][i] * float(lines[j][i])
                self.axes.plot(x, band1y, 'k+')
                for j in range(period/2+1,period):
                    band1y[j-period/2] = track2Band1[j][i] * float(lines[j][i])
                self.axes.plot(x, band1y, 'k+')
            if(Display_Band2):
                for j in range(period/2+1):
                    band2y[period/2-j]=track2Band2[j][i]*float(lines[j][i])
                self.axes.plot(x, band2y, 'k*')
                for j in range(period/2+1,period):
                    band2y[j-period/2] = track2Band2[j][i] * float(lines[j][i])
                self.axes.plot(x, band2y, 'k*')
        self.axes.plot(x, band1y, 'k+', label='First Band')
        self.axes.plot(x, band2y, 'k*', label='Second Band')
        self.axes.set_xlabel('k/(2$\pi$/%02ga)'%(NHole))
        self.axes.set_ylabel('$v_D$/(2$\pi$c/a)')
        # self.axes.plot(x, y, label='Second Band')
        if(Display_Legend):
            self.axes.legend(bbox_to_anchor=(1.05, 0), loc=3, borderaxespad=0.)
        self.axes.axis([min(x),max(x),miny,max(y)])
        # self.axes.plot(x, y, ',', label='Second Band')
        self.draw()

##############################################################################################################################################################################################
###00010
# Parameter Tree

# test subclassing parameters
# This parameter automatically generates two child parameters which are
# always reciprocals of each other
class ComplexParameter(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)

        self.addChild({'name': 'A = 1/B', 'type': 'float',
                       'value': 7, 'suffix': 'Hz', 'siPrefix': True})
        self.addChild({'name': 'B = 1/A', 'type': 'float',
                       'value': 1 / 7., 'suffix': 's', 'siPrefix': True})
        self.a = self.param('A = 1/B')
        self.b = self.param('B = 1/A')
        self.a.sigValueChanged.connect(self.aChanged)
        self.b.sigValueChanged.connect(self.bChanged)

    def aChanged(self):
        self.b.setValue(1.0 / self.a.value(), blockSignal=self.bChanged)

    def bChanged(self):
        self.a.setValue(1.0 / self.b.value(), blockSignal=self.aChanged)


# test add/remove
# this group includes a menu allowing the user to add new parameters into
# its child list
class ScalableGroup(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'group'
        opts['addText'] = "Add"
        opts['addList'] = ['str', 'float', 'int']
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self, typ):
        val = {
            'str': '',
            'float': 0.0,
            'int': 0
        }[typ]
        self.addChild(dict(name="ScalableParam %d" % (
            len(self.childs) + 1), type=typ, value=val, removable=True, renamable=True))


class ScalableGroup_Ref(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'group'
        opts['addText'] = "Add"
        opts['addList'] = ['str']
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self, typ):
        val = {
            'str': ' '
        }[typ]
        self.addChild(dict(name="ScalableParam %d" % (
            len(self.childs) + 1), type=typ, value=val, removable=True, renamable=True))

class ScalableGroup_Ref_Dis(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'group'
        opts['addText'] = "Add"
        opts['addList'] = ['bool']
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self, typ):
        val = {
            'bool': ' '
        }[typ]
        self.addChild(dict(name="ScalableParam %d" % (
            len(self.childs) + 1), type=typ, value=val, removable=True, renamable=True))


params = [

    {'name': 'Parameter Input', 'type': 'group', 'children': [
        {'name': 'NHole', 'type': 'int', 'value': 40, 'step': 1},
        {'name': 'Period', 'type': 'int', 'value': 34, 'step': 1},
        {'name': 'BandNum', 'type': 'int', 'value': 100, 'step': 1},
        {'name': 'CSV File Path', 'type': 'str',
            'value': './DataFile/Hole40-r0.1.csv'},
        {'name': 'CSV File Path Load', 'type': 'action'},

        {'name': 'First Band Start Point-[k,Band#]',
            'type': 'str', 'value': '[18,1]'},
        {'name': 'Second Band Start Point-[k,Band#]',
            'type': 'str', 'value': '[18,16]'},

        ScalableGroup_Ref(name="Reference", children=[
            {'name': 'Reference1 Name', 'type': 'str',
                'value': 'Reference First Band RROD=0.10 '},
            {'name': 'Reference1 Data', 'type': 'str',
                'value': '[0.0, 0.0251504, 0.0494593, 0.0717521, 0.0905083, 0.10496, 0.116102, 0.125494,0.134148, 0.14256, 0.150954, 0.159428, 0.168017, 0.176729, 0.185545, 0.194412, 0.203102, 0.208988]'},
            {'name': 'Reference2 Name', 'type': 'str',
                'value': 'Reference First Band RROD=0.25'},
            {'name': 'Reference2 Data', 'type': 'str',
                'value': '[0, 0.0252969, 0.0498416, 0.0726113, 0.092289, 0.108107, 0.120791, 0.131716, 0.141846,0.151657, 0.161344, 0.170954, 0.180446, 0.189696, 0.198452, 0.206208, 0.211974, 0.214207]'},
            {'name': 'Reference3 Name', 'type': 'str',
                'value': 'Reference Second Band RROD=0.10'},
            {'name': 'Reference3 Data', 'type': 'str',
                'value': '[0.123531, 0.124829, 0.128955, 0.136677, 0.149202, 0.167024, 0.18889, 0.212974,0.237945, 0.262836, 0.280369, 0.27083, 0.261153, 0.251537, 0.242014, 0.232643, 0.223651, 0.217664]'},
            {'name': 'Reference4 Name', 'type': 'str',
                'value': 'Reference Second Band RROD=0.25'},
            {'name': 'Reference4 Data', 'type': 'str',
                'value': '[0.124544, 0.125952, 0.130361, 0.138381, 0.150985, 0.168626, 0.190284, 0.214288,0.239337, 0.264467, 0.288292, 0.301733, 0.295688, 0.286956, 0.278316, 0.270572, 0.264797, 0.262559]'},
        ]),

        {'name': 'Input Save', 'type': 'action'},
    ]},
    {'name': 'Field Image Filter', 'type': 'group', 'children': [
        {'name': 'Field Image', 'type': 'str',
            'value': './DataFile/PNGlogfile'},
        {'name': 'Field Image Load', 'type': 'action'},
        {'name': 'Sort', 'type': 'action'},
        {'name': 'Unsort', 'type': 'action'},
        {'name': 'Repair', 'type': 'action'},
        {'name': 'Image Processor 1', 'type': 'action'},
        {'name': 'Image Processor 2', 'type': 'action'},
        {'name': 'Image Filter 1', 'type': 'bool','value':False},
        {'name': 'Image Filter 2', 'type': 'bool','value':False}

    ]},
    {'name': 'Display', 'type': 'group', 'children': [
        {'name': 'First Band', 'type': 'bool', 'value': True},
        {'name': 'Second Band', 'type': 'bool', 'value': True},
        {'name': 'Legend', 'type': 'bool', 'value': True},
        {'name':'Overlap Start Band','type':'int','value':55},
        {'name':'Overlap End Band','type':'int','value':62},
        ScalableGroup_Ref_Dis(name="Reference", children=[
            {'name': 'Reference1', 'type': 'bool', 'value': True},
            {'name': 'Reference2', 'type': 'bool', 'value': True},
            {'name': 'Reference3', 'type': 'bool', 'value': True},
            {'name': 'Reference4', 'type': 'bool', 'value': True},
        ]),
        {'name': 'Light Corn', 'type': 'bool', 'value': True},
        {'name': 'Brillouin Zone Boundary', 'type': 'bool', 'value': True},

        {'name': 'Display Save', 'type': 'action'},
        # {'name': 'Image Draw', 'type': 'action'},
    ]},
    {'name': 'Point Edit', 'type': 'group', 'children': [
        {'name': 'Fixed Point-First Band', 'type': 'text', 'value': ''},
        {'name': 'Fixed Point-Second Band', 'type': 'text', 'value': ''},#!!!!!!!
    ]},
    {'name': 'Output/Export', 'type': 'group', 'children': [
        {'name': 'Figure Output', 'type': 'action'},
        {'name': 'Image Field Export', 'type': 'action'},
        {'name': 'Data Export', 'type': 'action'}
    ]},

    {'name': 'Save/Restore functionality', 'type': 'group', 'children': [
        {'name': 'Save State', 'type': 'action'},
        {'name': 'Restore State', 'type': 'action', 'children': [
            {'name': 'Add missing items', 'type': 'bool', 'value': True},
            {'name': 'Remove extra items', 'type': 'bool', 'value': True},
        ]}
    ]}
]
print 'params',params
# Create tree of Parameter objects
p = Parameter.create(name='params', type='group', children=params)

# If anything changes in the tree, print a message

RepairFlag =0
Image1Stop=0
Image2Stop=0
def change(param, changes):
    global params
    global NHole
    global period
    global BandNum
    global csvpath
    global startpoint1_b
    global startpoint1_k
    global startpoint2_b
    global startpoint2_k
    global Ref2
    global Ref4
    global Ref1
    global Ref3
    global legend_Ref1
    global legend_Ref2
    global legend_Ref3
    global legend_Ref4
    global fieldpath
    global RepairFlag
    global Start_Band
    global End_Band
    global Display_Ref1
    global Display_Ref2
    global Display_Ref3
    global Display_Ref4
    global Display_Boundary
    global Display_Legend
    global Switch_Filter1
    global Switch_Filter2
    global Display_lightcorn

    print("tree changes:")
    for param, change, data in changes:
        path = p.childPath(param)
        if path is not None:
            childName = '.'.join(path)
        else:
            childName = param.name()
        print('  parameter: %s' % childName)
        print('  change:    %s' % change)
        print('  data:      %s' % str(data))
        print('  ----------')
        if(childName=='Parameter Input.NHole'):
            # params[0]['children'][0]['value']=data
            print params[0]['children'][0]['value']
            NHole = data
            print NHole
        elif(childName=='Parameter Input.Period'):
            params[0]['children'][1]['value']=data
            print params[0]['children'][1]['value']
            period = data
            print period
        elif(childName=='Parameter Input.BandNum'):
            params[0]['children'][2]['value']=data
            print params[0]['children'][2]['value']
            BandNum = data
            print BandNum
        elif(childName=='Parameter Input.CSV File Path'):
            params[0]['children'][3]['value']=str(data)
            print params[0]['children'][3]['value']
            csvpath=str(params[0]['children'][3]['value'])
            print csvpath
        elif(childName=='Parameter Input.CSV File Path Load'):
            path = QtGui.QFileDialog.getOpenFileName()
            print params[0]['children'][3]['value']
            if(path==''):
                pass
            else:
                params[0]['children'][3]['value']=str(path)
            print params[0]['children'][3]['value']
            csvpath=str(params[0]['children'][3]['value'])
        elif(childName=='Parameter Input.First Band Start Point-[k,Band#]'):
            params[0]['children'][5]['value']=data
            print params[0]['children'][5]['value']
            f = re.findall(r'\d+', data)
            startpoint1_k=int(f[0])
            startpoint1_b=int(f[1])
            print startpoint1_k,startpoint1_b
        elif(childName=='Parameter Input.Second Band Start Point-[k,Band#]'):
            params[0]['children'][6]['value']=data
            print params[0]['children'][6]['value']
            f = re.findall(r'\d+', data)
            startpoint2_k=int(f[0])
            startpoint2_b=int(f[1])
            print startpoint2_k,startpoint2_b
        elif(childName=='Parameter Input.Reference.Reference1 Name'):
            # params[1]['children'][0]['value']=data
            legend_Ref1=data
            print legend_Ref1
        elif(childName=='Parameter Input.Reference.Reference1 Data'):
            # params[1]['children'][0]['value']=data
            f = re.findall(r'\d*\.\d+',data)
            Ref1 = [float(f[0])]
            for i in range(len(f)-1):
                Ref1.append(float(f[i+1]))
            print Ref1
        elif(childName=='Parameter Input.Reference.Reference2 Name'):
            # params[1]['children'][0]['value']=data
            legend_Ref2=data
            print legend_Ref2
        elif(childName=='Parameter Input.Reference.Reference2 Data'):
            # params[1]['children'][0]['value']=data
            f = re.findall(r'\d*\.\d+',data)
            Ref2 = [float(f[0])]
            for i in range(len(f)-1):
                Ref2.append(float(f[i+1]))
            print Ref2
        elif(childName=='Parameter Input.Reference.Reference3 Name'):
            # params[1]['children'][0]['value']=data
            legend_Ref3=data
            print legend_Ref3
        elif(childName=='Parameter Input.Reference.Reference3 Data'):
            # params[1]['children'][0]['value']=data
            f = re.findall(r'\d*\.\d+',data)
            Ref3 = [float(f[0])]
            for i in range(len(f)-1):
                Ref3.append(float(f[i+1]))
            print Ref3
        elif(childName=='Parameter Input.Reference.Reference4 Name'):
            # params[1]['children'][0]['value']=data
            legend_Ref4=data
            print legend_Ref4
        elif(childName=='Parameter Input.Reference.Reference4 Data'):
            # params[1]['children'][0]['value']=data
            f = re.findall(r'\d*\.\d+',data)
            Ref4 = [float(f[0])]
            for i in range(len(f)-1):
                Ref4.append(float(f[i+1]))
            print Ref4
        elif(childName=='Field Image Filter.Field Image'):
            fieldpath=data
            print fieldpath
        elif(childName=='Field Image Filter.Field Image Load'):
            path = QtGui.QFileDialog.getExistingDirectory()
            print params[1]['children'][0]['value']
            if(path==''):
                fieldpath=params[1]['children'][0]['value']
                print 'You cancel the load...'
            else:
                fieldpath=str(path)
            print fieldpath
        elif(childName=='Field Image Filter.Sort'):
            subprocess.call("mkdir %s/FirstBand"%(fieldpath),shell=True)
            for i in range(1,BandNum+1):
                subprocess.call("mkdir %s/FirstBand/Band%02g"%(fieldpath,i),shell=True)
                subprocess.call("mv %s/*b%02g*.png %s/FirstBand/Band%02g"%(fieldpath,i,fieldpath,i),shell=True)
            subprocess.call("cp -R %s/FirstBand %s/SecondBand"%(fieldpath,fieldpath),shell=True)
            print 'Sort.. Done'
        elif(childName=='Field Image Filter.Unsort'):
            for i in range(1,BandNum+1):
                subprocess.call("mv %s/FirstBand/Band%02g/*.png %s"%(fieldpath,i,fieldpath),shell=True)
                subprocess.call("rm -rf %s/FirstBand/TrashBin/Band%02g"%(fieldpath,i),shell=True)
                subprocess.call("mv %s/SecondBand/Band%02g/*.png %s"%(fieldpath,i,fieldpath),shell=True)
                subprocess.call("rm -rf %s/SecondBand/Band%02g"%(fieldpath,i),shell=True)
            subprocess.call("rm -rf %s/FirstBand"%(fieldpath),shell=True)
            subprocess.call("rm -rf %s/SecondBand"%(fieldpath),shell=True)
            print 'Unsort.. Done'
        elif(childName=='Field Image Filter.Repair' and RepairFlag==0):
            print 'To Avoid some accident image loss, it is wise to Repair the image...'
            for i in range(1,BandNum+1):
                for k in range(1,period+2):
                    if(glob.glob('%s/FirstBand/Band%02g/*h.k%02g.b%02g*.png  '%(fieldpath,i,k,i))):
                        pass
                    else:
                        subprocess.call("cp %s/FirstBand/Band01/*h.k%02g.b01*.png %s/FirstBand/Band%02g/h.k%02g.b%02g.png"%(fieldpath,period/2+1,fieldpath,i,k,i),shell=True)
                    if(glob.glob('%s/Band%02g/SecondBand/*h.k%02g.b%02g*.png  '%(fieldpath,i,k,i))):
                        pass
                    else:
                        subprocess.call("cp %s/SecondBand/Band01/*h.k%02g.b01*.png %s/SecondBand/Band%02g/h.k%02g.b%02g.png"%(fieldpath,period/2+1,fieldpath,i,k,i),shell=True)
            print 'Repair.. Done'
            RepairFlag=1
        elif(childName=='Field Image Filter.Repair' and RepairFlag==1):
            print "To Avoid problems, Repair Function can only be done once."
        elif(childName=='Field Image Filter.Image Processor 1'):
            # imageprocessor1
            import cv2.cv as cv
            subprocess.call("mkdir %s/FirstBand/TrashBin"%(fieldpath),shell=True)
            for j in range(1, 40):
                for i in range(1, period+1):
                    if(glob.glob('%s/FirstBand/Band%02g/*h.k%02g.b%02g*.png' % (fieldpath,j, i , j))):
                        exact_name=glob.glob('%s/FirstBand/Band%02g/*h.k%02g.b%02g*.png' % (fieldpath,j, i , j))[0]
                        image = cv.LoadImage('%s' % (exact_name))
                        new = cv.CreateImage(cv.GetSize(image), image.depth, 1)
                        for imh in range(image.height):
                            for imw in range(image.width):
                                new[imh, imw] = (image[imh, imw][0]+image[imh, imw][1]+image[imh, imw][2])/3
                        cv.Threshold(new, new, 230, 255, cv.CV_THRESH_BINARY_INV)
                        sumx = []
                        # print sumx
                        for x in range(image.height/2):
                            sum = 0
                            for y in range(image.width):
                                sum += new[x, y]
                            if(sum == 0):
                                sumx.append(x)
                        # print sumx
                        if(sumx<>[] and min(sumx)>90):
                            subprocess.call('mv %s/SecondBand/Band%02g/*h.k%02g.b%02g*.png %s/SecondBand/TrashBin' % (fieldpath,j, i, j,fieldpath), shell=True)
                    else:
                        print "No Found", i, j
            print "Image Processor 1 Done"
        elif(childName=='Field Image Filter.Image Processor 2'):
            # imageprocessor2
            import cv2.cv as cv
            subprocess.call("mkdir %s/SecondBand/TrashBin"%(fieldpath),shell=True)
            coun=0
            for j in range(startpoint2_b, BandNum+1):
                for i in range(1, period+1):        
                    if(glob.glob('%s/SecondBand/Band%02g/*h.k%02g.b%02g*.png' % (fieldpath,j, i , j))):
                        exact_name=glob.glob('%s/SecondBand/Band%02g/*h.k%02g.b%02g*.png' % (fieldpath,j, i , j))[0]
                        image = cv.LoadImage('%s' % (exact_name))
                        new = cv.CreateImage(cv.GetSize(image), image.depth, 1)
                        for imh in range(image.height):
                            for imw in range(image.width):
                                new[imh, imw] = (image[imh, imw][0] + image[imh, imw]
                                                 [1] + image[imh, imw][2]) / 3
                        cv.Threshold(new, new, 220, 255, cv.CV_THRESH_BINARY_INV)
                        sumx = []
                        for x in range(100):
                            sum = 0
                            for y in range(image.width):
                                sum += new[x, y]
                            if(sum == 0):
                                sumx.append(x)
                        if(sumx <> []):
                            if(max(sumx) < 80 and min(sumx) > 40):
                                print "i j=", i, j
                                subprocess.call('mv %s/SecondBand/Band%02g/*h.k%02g.b%02g*.png %s/SecondBand/TrashBin' % (fieldpath,j, i, j,fieldpath), shell=True)
                    else:
                        print "No Found", i, j
            print "Image Processor 2 Done"
        elif(childName=='Field Image Filter.Image Filter 1'):
            Switch_Filter1=data
            print Switch_Filter1
        elif(childName=='Field Image Filter.Image Filter 2'):
            Switch_Filter2=data
            print Switch_Filter2
        elif(childName=='Display.Overlap Start Band'):
            Start_Band=data
            print Start_Band
        elif(childName=='Display.Overlap End Band'):
            End_Band=data
            print End_Band
        elif(childName=='Display.Brillouin Zone Boundary'):
            Display_Boundary=data
        elif(childName=='Display.Light Cron'):
            Display_lightcorn=data
        elif(childName=='Display.Legend'):
            Display_Legend=data
        elif(childName=='Output/Export.Figure Output'):
            fig.Band1Data()
            fig.Band2Data()
            sc.axes.cla()
            sc.f1Plot(x=arange(0,0.5+0.5/(len(Band1)-1),0.5/(len(Band1)-1)),y=Band1)
            sc.f2Plot(x=arange(0,0.5+0.5/(len(Band2)-1),0.5/(len(Band2)-1)),y=Band2)
            if(Display_Ref1):
                sc.fxPlot(x=arange(0,0.5+0.5/(len(Ref1)-1),0.5/(len(Ref1)-1)),y=Ref1,l=legend_Ref1)
            if(Display_Ref2):
                sc.fxPlot(x=arange(0,0.5+0.5/(len(Ref2)-1),0.5/(len(Ref2)-1)),y=Ref2,l=legend_Ref2)
            if(Display_Ref3):
                sc.fxPlot(x=arange(0,0.5+0.5/(len(Ref3)-1),0.5/(len(Ref3)-1)),y=Ref3,l=legend_Ref3)
            if(Display_Ref4):
                sc.fxPlot(x=arange(0,0.5+0.5/(len(Ref4)-1),0.5/(len(Ref4)-1)),y=Ref4,l=legend_Ref4)
            if(Display_Boundary):
                sc.plot_Boundary()
            if(Display_lightcorn):
                sc.plot_lightcorn()
            if(Display_Legend):
                sc.axes.legend(bbox_to_anchor=(1.05, 0), loc=3, borderaxespad=0.)
            sc2.axes.cla()
            sc2.OverlapBand(start_band=Start_Band,end_band=End_Band)
            sc2.axes.set_xlabel('k/(2$\pi$/%02ga)'%(NHole))
            sc2.axes.set_ylabel('$v_D$/(2$\pi$c/a)')

        elif(childName=='Output/Export.Image Field Export'):
            subprocess.call("rm -rf %s/Band1Field"%(fieldpath), shell=True)
            subprocess.call("rm -rf %s/Band1dpwr"%(fieldpath), shell=True)
            subprocess.call("rm -rf %s/Band2Field"%(fieldpath), shell=True)
            subprocess.call("rm -rf %s/Band2dpwr"%(fieldpath), shell=True)
            subprocess.call("mkdir %s/Band1Field"%(fieldpath), shell=True)
            subprocess.call("mkdir %s/Band1dpwr"%(fieldpath), shell=True)
            subprocess.call("mkdir %s/Band2Field"%(fieldpath), shell=True)
            subprocess.call("mkdir %s/Band2dpwr"%(fieldpath), shell=True)
            for i in range(0, len(Band1)):
                subprocess.call("cp %s/FirstBand/Band%02g/*h.k%02g.b%02g*.png %s/Band1Field/h.%03g.k%02g.b%02g.png"%(fieldpath, track1Band1[i][1],int((i+period/2)%period+1), track1Band1[i][1],fieldpath, i, int((i+period/2)%period+1), track1Band1[i][1]), shell=True)
                subprocess.call("cp %s/FirstBand/Band%02g/*dpwr.k%02g.b%02g*.png %s/Band1dpwr/dpwr.%03g.k%02g.b%02g.png"%(fieldpath,track1Band1[i][1], int((i+period/2)%period+1), track1Band1[i][1], fieldpath,i, int((i+period/2)%period+1), track1Band1[i][1]), shell=True)
            for i in range(0, len(Band2)):
                subprocess.call("cp %s/SecondBand/Band%02g/*h.k%02g.b%02g*.png %s/Band2Field/h.%03g.k%02g.b%02g.png" %
                                (fieldpath, track1Band2[i][1],int((i+period/2)%period+1), track1Band2[i][1],fieldpath, i, int((i+period/2)%period+1), track1Band2[i][1]), shell=True)
                subprocess.call("cp %s/SecondBand/Band%02g/*dpwr.k%02g.b%02g*.png %s/Band2dpwr/dpwr.%03g.k%02g.b%02g.png" %
                                (fieldpath,track1Band2[i][1], int((i+period/2)%period+1), track1Band2[i][1], fieldpath,i, int((i+period/2)%period+1), track1Band2[i][1]), shell=True)
        elif(childName=='Output/Export.Data Export'):
            Data_Export()
        elif(childName=='Point Edit.Fixed Point-First Band'):
            print data
            Text_Transform_Band1Fixed(s=data)
        elif(childName=='Point Edit.Fixed Point-Second Band'):
            print data
            Text_Transform_Band2Fixed(s=data)
        elif(childName=='Display.Reference.Reference1'):
            Display_Ref1=data
        elif(childName=='Display.Reference.Reference2'):
            Display_Ref2=data
        elif(childName=='Display.Reference.Reference3'):
            Display_Ref3=data
        elif(childName=='Display.Reference.Reference4'):
            Display_Ref4=data
# p.sigTreeStateChanged.connect(change)

def valueChanging(param, value):
    print("Value changing (not finalized): %s %s" % (param, value))

# Too lazy for recursion:
for child in p.children():
    child.sigValueChanging.connect(valueChanging)
    for ch2 in child.children():
        ch2.sigValueChanging.connect(valueChanging)


def save():
    global state
    state = p.saveState()

def restore():
    global state
    add = p['Save/Restore functionality', 'Restore State', 'Add missing items']
    rem = p['Save/Restore functionality',
            'Restore State', 'Remove extra items']
    p.restoreState(state, addChildren=add, removeChildren=rem)
p.param('Save/Restore functionality', 'Save State').sigActivated.connect(save)
p.param('Save/Restore functionality',
        'Restore State').sigActivated.connect(restore)


# Create two ParameterTree widgets, both accessing the same data
t = ParameterTree()
t.setParameters(p, showTop=False)
# t.setWindowTitle('pyqtgraph example: Parameter Tree')

# test save/restore
s = p.saveState()
p.restoreState(s)


##############################################################################################################################################################################################
###00010
##ApplicationWindow
class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        win = QtGui.QMainWindow()

        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        area = DockArea()
        self.setCentralWidget(area)
        self.resize(900, 600)

        d1 = Dock("Parameter Dock", size=(200, 600))
        d2 = Dock("Figure Dock", size=(600, 600))
        # d3 = Dock("Console", size=(100, 600))

        area.addDock(d1, 'left')
        area.addDock(d2, 'right', d1)
        # area.addDock(d3, 'right', d2)
        # w1 = pg.LayoutWidget()
        # label = QtGui.QLabel(""" -- DockArea Example --
        # This window has 6 Dock widgets in it. Each dock can be dragged
        # by its title bar to occupy a different space within the window
        # but note that one dock has its title bar hidden). Additionally,
        # the borders between docks may be dragged to resize. Docks that are dragged on top
        # of one another are stacked in a tabbed layout. Double-click a dock title
        # bar to place it in its own window.
        # """)
        # label = QtGui.QLabel(""" -- DockArea Example --""")
        # saveBtn = QtGui.QPushButton('Save dock state')
        # restoreBtn = QtGui.QPushButton('Restore dock state')
        # csvLoadBtn = QtGui.QPushButton('csvfile Load')
        # f1LoadBtn = QtGui.QPushButton('Field1 ImageFile Load')
        # f2LoadBtn = QtGui.QPushButton('Field2 ImageFile Load')
        # UpdateBtn = QtGui.QPushButton('Update')
        # restoreBtn.setEnabled(False)
        # w1.addWidget(label, row=0, col=0)
        # w1.addWidget(saveBtn, row=10, col=0)
        # w1.addWidget(restoreBtn, row=20, col=0)
        # w1.addWidget(csvLoadBtn, row=30, col=0)
        # w1.addWidget(f1LoadBtn, row=40, col=0)
        # w1.addWidget(f2LoadBtn, row=50, col=0)
        # w1.addWidget(UpdateBtn, row=60, col=0)
        # d1.addWidget(w1)
        # w3=pg.LayoutWidget()
        # txb=pg.TextItem(text='', color=(200, 200, 200), html=None, anchor=(0, 0), border=None, fill=None, angle=0)
        # w3.addWidget(txb)
        # d3.addWidget(w3)

        # Layout Area Save and Restore
        # state = None

        # def save():
        #     global state
        #     state = area.saveState()
        #     restoreBtn.setEnabled(True)

        # def load():
        #     global state
        #     area.restoreState(state)

        # saveBtn.clicked.connect(save)
        # restoreBtn.clicked.connect(load)

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)

        global fig
        global sc
        global sc2
        fig = MyMplCanvas()
        fig.DisplaySwitch_Init()
        fig.Band1Data()
        sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        sc.f1Plot(x=arange(0,0.5+0.5/(len(Band1)-1),0.5/(len(Band1)-1)),y=Band1)
        fig.Band2Data()
        sc.f2Plot(x=arange(0,0.5+0.5/(len(Band2)-1),0.5/(len(Band2)-1)),y=Band2)
        if(Display_Ref1):
            sc.fxPlot(x=arange(0,0.5+0.5/(len(Ref1)-1),0.5/(len(Ref1)-1)),y=Ref1,l=legend_Ref1)
        if(Display_Ref2):
            sc.fxPlot(x=arange(0,0.5+0.5/(len(Ref2)-1),0.5/(len(Ref2)-1)),y=Ref2,l=legend_Ref2)
        if(Display_Ref3):
            sc.fxPlot(x=arange(0,0.5+0.5/(len(Ref3)-1),0.5/(len(Ref3)-1)),y=Ref3,l=legend_Ref3)
        if(Display_Ref4):
            sc.fxPlot(x=arange(0,0.5+0.5/(len(Ref4)-1),0.5/(len(Ref4)-1)),y=Ref4,l=legend_Ref4)
        if(Display_Boundary):
            sc.plot_Boundary()
            print '!!!!!!!!!!!!!'
        if(Display_lightcorn):
            sc.plot_lightcorn()
        fig1.canvas.mpl_connect('button_press_event', Canvas_onclick)
        if(Display_Legend):
            sc.axes.legend(bbox_to_anchor=(1.05, 0), loc=3, borderaxespad=0.)
        sc2 =MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        sc2.OverlapBand(start_band=55,end_band=62)



        p.sigTreeStateChanged.connect(change)



        # def update_dc():
        #     global dc
        #     global csvpathtextbox, f1ImageLoad, f2ImageLoad
        #     label = QtGui.QLabel(csvpathtextbox.text())
        #     w1.addWidget(label, row=70, col=0)

        #     dc = MyDynamicMplCanvas(
        #         self.main_widget, width=5, height=4, dpi=100)

        #     d2.addWidget(dc, row=0, col=1)

        # UpdateBtn.clicked.connect(update_dc)
        # l1.addWidget(sc)
        # d1.addWidget(l1)
        # d1.addWidget(sc)
        d1.addWidget(t)
        d2.addWidget(sc, row=0, col=0)
        navi1 = NavigationToolBar(sc,self)
        d2.addWidget(navi1,row=1,col=0)
        d2.addWidget(sc2,row=2, col=0)
        navi2 = NavigationToolBar(sc2,self)
        d2.addWidget(navi2,row=3,col=0)
        # d2.addWidget(dc, row=0, col=1)
        # l.addWidget(dc)

        self.main_widget.setFocus()
        # self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About",
                                """embedding_in_qt4.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale

This program is a simple example of a Qt4 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation."""
                                )

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
# qApp.exec_()
    