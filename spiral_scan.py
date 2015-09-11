from __future__ import absolute_import
from __future__ import print_function, division
from math import *
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import *
import time

stepAngle = 0.25 * pi
phi = pi
maxSize = 50
step = 0.2 * maxSize
r = step
z = 0
IN = 0
OUT = 1
rDir = OUT

xvector = []
yvector = []
zvector = []

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

ax.scatter(maxSize / 2, maxSize / 2, z, zdir='z', c= 'red')
plt.draw()

icolor = 0
epsilon = 0.001

while (z <= maxSize):
    if r > maxSize / 2:
        stepAngle = (stepAngle * r) / (r - step)

#        stepAngle = (stepAngle * (r + step)) / r
        r -= step
        rDir = IN
    else:
        #stepAngle = (stepAngle * r) / (r + step)
        stepAngle = 0.25 * pi

        r = step
        rDir = OUT

        x = y = maxSize / 2
        xvector.append(x)
        yvector.append(y)
        zvector.append(z)
        if (icolor % 2 == 0):
            ax.scatter(x, y, z, zdir='z', c= 'red')
        else:
            ax.scatter(x, y, z, zdir='z', c= 'blue')
        plt.draw()

    while ((r > step or abs(r - step) < epsilon) and (r < maxSize / 2 or abs(r - maxSize / 2) < epsilon)):
        while (phi > -pi):

            x = r * cos(phi) + maxSize / 2
            y = r * sin(phi) + maxSize / 2

            xvector.append(x)
            yvector.append(y)
            zvector.append(z)

            if (icolor % 2 == 0):
                ax.scatter(x, y, z, zdir='z', c= 'red')
            else:
                ax.scatter(x, y, z, zdir='z', c= 'blue')
            plt.draw()
            time.sleep(0.0000001)

            phi -= stepAngle

        print('B', icolor, stepAngle, r)


        if (rDir == IN):
            #stepAngle = (stepAngle * (2 * r + 2 * step)) / (2 * r)
            if (abs(r - step) > epsilon):
                stepAngle = (stepAngle * r) / (r - step)

            r -= step
        else:
            #stepAngle = (stepAngle * 2 * r) / (2 * r + 2 * step)
            stepAngle = (stepAngle * r) / (r + step)
            r += step

        print('A', icolor, stepAngle, r)

        phi = pi


    if (rDir == IN):
        x = y = maxSize / 2
        xvector.append(x)
        yvector.append(y)
        zvector.append(z)
        if (icolor % 2 == 0):
            ax.scatter(x, y, z, zdir='z', c= 'red')
        else:
            ax.scatter(x, y, z, zdir='z', c= 'blue')
        plt.draw()

    z += step

    icolor += 1


plt.hold(True)


#plt.plot(xvector, yvector)
#plt.axis([- maxSize / 2, maxSize / 2, - maxSize / 2, maxSize / 2])
plt.show()
