from __future__ import absolute_import
from numpy import *
from mpl_toolkits.mplot3d import *
from matplotlib import pyplot as plt
import time

i = 0
j = 0
k = 0
maxSize = 5
step = 1
xscan = []
yscan = []
zscan = []

'''
Constants
'''
RIGHT = 0
LEFT = 1
DOWN = 0
UP = 1


kDir = RIGHT
jDir = DOWN

fig = plt.figure()
ax = fig.gca(projection='3d')               # to work in 3d
#plt.axes([0, maxSize, 0, maxSize])
ax.set_xlim3d(0, maxSize)
ax.set_ylim3d(0, maxSize)
ax.set_zlim3d(0, maxSize)

ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')

plt.ion()
plt.show()

while (i <= maxSize):
    if j > maxSize:
        j = maxSize
        jDir = UP
    if j < 0:
        j = 0
        jDir = DOWN
    while (j >= 0 and j <= maxSize):
        if k > maxSize:
            k = maxSize
            kDir = LEFT
        if k < 0:
            k = 0
            kDir = RIGHT
        while (k >= 0 and k <= maxSize):
            xscan.append(k)
            yscan.append(j)
            zscan.append(i)

            #ax = fig.gca(projection='3d')               # to work in 3d
            ax.scatter(k, j, i, zdir='z', c= 'red')
            plt.draw()
            time.sleep(0.01)

            if kDir == RIGHT:
                k += step
            else:
                k -= step
        if jDir == DOWN:
            j += step
        else:
            j -= step
    i += step

#fig = plt.figure()
#ax = fig.gca(projection='3d')               # to work in 3d
#ax = fig.add_subplot(222, projection='3d')
#ax.plot(xscan, yscan, zscan, zdir='z', c= 'red')
plt.hold(True)
#plt.show()
