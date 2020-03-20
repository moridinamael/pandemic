# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 22:29:46 2019

@author: Matt
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 13:58:42 2019

@author: mfreeman
"""

import math
import time
from PIL import ImageGrab
import random
from Tkinter import *

def draw_circle(r,xcenter,ycenter):
    yarray,xarray = [],[]
    for xx in range(int(-1.0*r),r+1):
        xarray.append(xx+xcenter)
        yarray.append(math.sqrt(r*r-xx*xx)+ycenter)

    for xx in reversed(range(int(-1.0*r),r+1)):
        xarray.append(xx+xcenter)
        yarray.append(-1.0*math.sqrt(r*r-xx*xx)+ycenter)

    return zip(xarray,yarray)



def rotate_pivot(pointx,pointy,pivotx,pivoty,angle):
    s = math.sin(angle)
    c = math.cos(angle)
    xshift = pointx-pivotx
    yshift = pointy-pivoty
    xnew   = xshift*c - yshift*s
    ynew   = xshift*s + yshift*c
    newpoint_x = xnew+pivotx
    newpoint_y = ynew+pivoty
    return newpoint_x,newpoint_y

def move_straight(pointx,pointy,vx,vy,sidebounce,topbounce):
    if topbounce == True:
        vy = -vy
    if sidebounce == True:
        vx = -vx

    xshift = pointx-vx
    yshift = pointy-vy
    return xshift,yshift,vx,vy

def proxy(x,y,other_cx,other_cy,first_axis):
    contagion_dist = 10.0
    for key in other_cx:
        _xp,_yp,_vx,_vy,inf_timer,obj,quarantine = first_axis[key]
        xp = other_cx[key]
        yp = other_cy[key]
        r = math.sqrt((x - xp)*(x - xp) + (y - yp)*(y - yp))
        if r < contagion_dist and r != 0.0 and inf_timer > 0.0 and quarantine == False:
            return True
    return False

class Game:
    def __init__(self, gameWidth, gameHeight):
        self.root = Tk()
        self.gameWidth = gameWidth
        self.gameHeight = gameHeight
        self.gameWindow()
        
        self.x0 = self.gameWidth/2
        self.y0 = self.gameHeight/2

        first_axis = {}
        moonmap = {}

        population = 100
        infection_rate = 0.10
        for n in range(0,population):

            r = 2.0
            tag = "mover"+str(n)
            cmx,cmy = random.random()*500+250,random.random()*500+250 #
            vx,vy = (random.random()-0.5),(random.random()-0.5)
            cm = draw_circle(int(r),cmx,cmy)
            if(random.random() < infection_rate):
                infection_timer = 1.0
                color = "red"
            else:
                infection_timer = 0.0
                color = "white"
            obj = self.canvas.create_polygon(cm, outline=color, width=3, tags=tag)
            first_axis[tag] = [cmx,cmy,vx,vy,infection_timer,obj,False]

        leftbarrier = 250
        rightbarrier = 750
        topbarrier = 250
        bottombarrier = 750
        self.canvas.create_polygon(draw_circle(int(r),rightbarrier,bottombarrier), outline="green", width=3, tags="box1")
        self.canvas.create_polygon(draw_circle(int(r),leftbarrier,bottombarrier), outline="green", width=3, tags="box2")
        self.canvas.create_polygon(draw_circle(int(r),rightbarrier,topbarrier), outline="green", width=3, tags="box3")
        self.canvas.create_polygon(draw_circle(int(r),leftbarrier,topbarrier), outline="green", width=3, tags="box4")

        #print first_axis
        
        currentcx,currentcy,currentvx,currentvy,prevx,prevy = {},{},{},{},{},{}

        for planet in first_axis:
            cmx,cmy,vmx,vmy,inftimer,obj,quarantine = first_axis[planet]
            currentcx[planet],currentcy[planet],currentvx[planet],currentvy[planet] = cmx,cmy,vmx,vmy
            prevx[planet],prevy[planet]=cmx,cmy

        for kk in range(0,5000):

            for planet in first_axis:
                cmx,cmy,vmx,vmy,inf_timer,obj,quarantine = first_axis[planet]
                if(planet in moonmap):
                    ctr_x,ctr_y = currentcx[moonmap[planet]],currentcy[moonmap[planet]]
                    #prevx[planet],prevy[planet]=currentcx[moonmap[planet]],currentcy[moonmap[planet]]
                else:
                    ctr_x,ctr_y = self.x0,self.y0
                        
                sidebounce = False
                topbounce = False
                if( abs(currentcx[planet] - rightbarrier) <= 1.0 or abs(currentcx[planet] - leftbarrier) <= 1.0):
                    sidebounce = True
                if( abs(currentcy[planet] - topbarrier) <= 1.0 or abs(currentcy[planet] - bottombarrier) <= 1.0):
                    topbounce = True
    
                    
                proxflag = proxy(currentcx[planet],currentcy[planet],currentcx,currentcy,first_axis)
                if proxflag == True:
                    if first_axis[planet][4] != 0.0:
                        pass
                    else:
                        self.canvas.itemconfig(obj,outline = "red")
                        first_axis[planet][4] = 1.0
                    
                disease_decay_rate = 0.0009
                if(first_axis[planet][4] > 0.0):
                    first_axis[planet][4] -= disease_decay_rate
                    
                if first_axis[planet][4] < 0.0:
                    self.canvas.itemconfig(obj,outline = "blue")
                    
                # Good curve-flattening number
                #daily_test_prob = 0.002
                # Good extinction number
                #daily_test_prob = 0.006
                # Aggressive extinction
                daily_test_prob = 0.01     
                
                if first_axis[planet][6] == True and first_axis[planet][4] <= 0.0:
                    first_axis[planet][6] = False
                if(random.random() < daily_test_prob):
                    if first_axis[planet][4] > 0.0:
                        self.canvas.itemconfig(obj,outline = "violet")
                        first_axis[planet][6] = True
                    
                if first_axis[planet][6] == True: print "Quarantine", first_axis[planet][6]
                if first_axis[planet][6] == False:
                    currentcx[planet],currentcy[planet],currentvx[planet],currentvy[planet] = move_straight(currentcx[planet],currentcy[planet],currentvx[planet],currentvy[planet],sidebounce,topbounce)
                    self.canvas.move(planet,currentcx[planet]-prevx[planet],currentcy[planet]-prevy[planet])
                    prevx[planet],prevy[planet]=currentcx[planet],currentcy[planet]

                    


            time.sleep(0.01)
            self.canvas.update()

        self.root.destroy()


    def gameWindow(self):
        self.frame = Frame(self.root)
        self.frame.pack(fill=BOTH, expand=YES)

        self.canvas = Canvas(self.frame,width=self.gameWidth, height=self.gameHeight, bg="black", takefocus=1)
        self.canvas.pack(fill=BOTH, expand=YES)

asteroids = Game(1000,1000) #300,300)