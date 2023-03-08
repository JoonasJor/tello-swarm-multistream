import keyModule as km
from djitellopy import tello, TelloSwarm
from time import sleep
import numpy as np
import cv2
import math

# PARAMETERS
fSpeed = 117 / 10  # Forward speed in cm/s (15cm/s)
aSpeed = 360 / 10  # Angular speed  degrees/s (50d/s)
interval = 0.25  # Defines often distance is being printed

dInterval = fSpeed * interval
aInterval = aSpeed * interval
x = [500, 550]
y = [500, 500]
a = 0
yaw = 0
coordinates = [[(x[0], y[0])], [(x[1], y[1])]]
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]

drone = 9

km.init()

swarm = TelloSwarm.fromIps([
    "192.168.73.110",
    "192.168.73.165"
])
# me = tello.Tello()
swarm.connect()

for tello in swarm:
    print(tello.get_battery())


# print(me.get_battery())


# cv2.imshow("Output", img)
# cv2.waitKey(1)

def getKeyBoardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 30
    aspeed = 50
    global yaw, x, y, a, drone
    d = 0
    if km.getkey("LEFT"):
        lr = -speed
        d = dInterval
        a = -180

    elif km.getkey("RIGHT"):
        lr = speed
        d = -dInterval
        a = 180

    if km.getkey("UP"):
        fb = speed
        d = dInterval
        a = 270
            
    elif km.getkey("DOWN"):
        fb = -speed
        d = -dInterval
        a = -90

    if km.getkey("w"):
        ud = speed

    elif km.getkey("s"):
        ud = -speed

    if km.getkey("a"):
        yv = -aspeed
        yaw -= aInterval      
        print(yv)
        print(yaw)

    elif km.getkey("d"):
        yv = aspeed
        yaw += aInterval    
        print(yv)
        print(yaw)

    if km.getkey("q"):
        swarm.land()
    if km.getkey("e"):
        swarm.takeoff()
    if km.getkey("0"):
        drone = 0
    elif km.getkey("1"):
        drone = 1
    elif km.getkey("9"):
        drone = 9

    sleep(interval)

    a += yaw
    if(drone == 9):
        for i in range(len(swarm.tellos)):
            x[i] += int(d * math.cos(math.radians(a)))
            y[i] += int(d * math.sin(math.radians(a)))          
    else:
        x[drone] += int(d * math.cos(math.radians(a)))
        y[drone] += int(d * math.sin(math.radians(a)))   
    return [lr, fb, ud, yv]


def drawPoints():
    for d in range(len(swarm.tellos)):      
        for i in range(len(coordinates[d])):
            cv2.circle(img, coordinates[d][i], 2, colors[d], cv2.FILLED)       
        cv2.putText(img, f'({(x[d] - 500) / 100}, {(y[d] - 500) / 100})m', (x[d] + 10, y[d] + 30), cv2.FONT_HERSHEY_PLAIN, 1, colors[d], 1)

while True:
    vals = getKeyBoardInput()

    if (drone == 9):
        swarm.send_rc_control(vals[0], vals[1], vals[2], vals[3])
        for d in range(len(swarm.tellos)):
            coordinates[d].append((x[d], y[d]))
    else:
        swarm.send_rc_control(0, 0, 0, 0)
        swarm.tellos[drone].send_rc_control(vals[0], vals[1], vals[2], vals[3])
        coordinates[drone].append((x[drone], y[drone]))       

    img = np.zeros((1000, 1000, 3), np.uint8)
    drawPoints()
    cv2.imshow("Output", img)
    cv2.waitKey(1)
