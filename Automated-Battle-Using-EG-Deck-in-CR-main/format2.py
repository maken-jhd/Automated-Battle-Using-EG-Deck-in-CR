from placeCard import placeCardN
from getCycle import init5
from changeCycle import changeCycle
from comCycle import CRCardCycle
import time
cycle = CRCardCycle()
def formatEG1x(delay,random,line):
    r = random % 2
    if line == 1:
        placeCardN("EGolem",r)
        time.sleep(delay / 2)
    elif line == 2:
        placeCardN("NWitch",r)
        time.sleep(delay * 2)
    elif line == 3:
        placeCardN("GRobot",9-r)
        time.sleep(delay)
    elif line == 4:
        placeCardN("rage",10+r)
        time.sleep(delay)
    elif line == 5:
        placeCardN("sk",4 + r)
        time.sleep(delay / 2)
    elif line == 6:
        placeCardN("archer",4 + r)
def formatEG2x(delay,random,line):
    r = random % 2
    if line == 1:
        placeCardN("EGolem",r)
        time.sleep(delay / 2)
    elif line == 2:
        placeCardN("NWitch",r)
        time.sleep(delay * 2.5)
    elif line == 3:
        placeCardN("Ksk",1-r)
        time.sleep(delay *2)
    elif line == 4:
        placeCardN("GRobot",8 + r)
        time.sleep(delay / 4)
    elif line == 5:
        placeCardN("sk",5-r)
        time.sleep(delay / 2)
    elif line == 6:
        placeCardN("archer",7-r)
        time.sleep(delay * 1.5)
    elif line == 7:
        placeCardN("rage",10+r)
        time.sleep(delay * 3)
def formatEG3x(delay,random,line):
    r = random % 2
    if line == 1:   
        placeCardN("EGolem",4 + r)
        time.sleep(delay)
    elif line == 2:
        placeCardN("NWitch",4 + r)
        time.sleep(delay * 3.2)
    elif line == 3:
        placeCardN("GRobot",8+r)
        time.sleep(delay * 2)
    elif line == 4:
        placeCardN("Ksk",3-r)#need to add True AFTER TEST
        time.sleep(delay)
    elif line == 5:
        placeCardN("sk",5-r)
        time.sleep(delay)
    elif line == 6:
        placeCardN("EGolem",9-r)
        time.sleep(delay * 1.5)
    elif line == 7:
        placeCardN("archer",7-r)
        time.sleep(delay * 1.5)
    elif line == 8:
        placeCardN("rage",10+r)
        time.sleep(delay * 1.5)
    elif line == 9:
        placeCardN("arrows", 11-r)
        time.sleep(delay)
    elif line == 10:
        placeCardN("sk",4+r)
if __name__ == "__main__":
    t0 = time.perf_counter()
    init5()
    cycle.show_all()
    changeCycle()
    cycle.show_all()
    #'''
    formatEG1x(6,0)
    time.sleep(12)
    t1 = time.perf_counter()
    if t1 - t0 < 90:
        formatEG1x(6,1)
        time.sleep(9)
    else:
    #placeCardN("arrows",11)
        time.sleep(12)
    #'''
    #'''
    for i in range(4):
        time.sleep(2)
        formatEG2x(3,i)
    #'''
    for i in range(3):
        formatEG3x(2,i)
    