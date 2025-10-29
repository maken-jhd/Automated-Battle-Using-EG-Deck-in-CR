from comCycle import CRCardCycle
from placeCard import placeCardN
from getCycle import init5
import time
cycle = CRCardCycle()
delay = 6
def rigthCycle():
    rights = 0
    if cycle.find_card("EGolem") != [] and cycle.find_card("EGolem")[0]["type"] == "available":
        rights = rights + 1
    if cycle.find_card("NWitch") != [] and cycle.find_card("NWitch")[0]["position"] < 6:
        rights = rights + 1
    if cycle.find_card("GRobot") != [] and cycle.find_card("GRobot")[0]["position"] < 7:
        rights = rights + 1
    if cycle.find_card("Ksk") != [] and cycle.find_card("Ksk")[0]["position"] < 8:
        rights = rights + 1
    if cycle.find_card("rage") != [] and cycle.find_card("rage")[0]["position"] < 8:
        rights = rights + 1
    if rights == 5:
        return True
    else:
        return False
def changeCycle():
    guess = False
    t0 = time.perf_counter()
    while not rigthCycle():
        delay = 6
        if cycle.find_card("rage") != [] and cycle.find_card("rage")[0]["type"] == "available":
            placeCardN("rage",10)
            delay = 4
        elif cycle.find_card("sk") != [] and cycle.find_card("sk")[0]["type"] == "available":
            placeCardN("sk",0)
            delay = 2
        elif cycle.find_card("archer") != [] and cycle.find_card("archer")[0]["type"] == "available":
            placeCardN("archer",0)
        elif cycle.find_card("arrows") != [] and cycle.find_card("arrows")[0]["type"] == "available":
            placeCardN("arrows",10)
        elif cycle.find_card("Unknown") != [] and cycle.find_card("Unknown")[0]["type"] == "available":
            if not guess:
                placeCardN("Unknown",0)
                guess = True
            else:
                cycle.set_card(cycle.find_card("Unknown")[0]["position"],"Unknown",0.0,True)
                delay = 0
        else:
            placeCardN("NWitch",0)
            delay = 8
        if rigthCycle():
            delay = delay / 2
        time.sleep(delay)
        t1 = time.perf_counter()
        if t1 - t0 > 90:
            return False
    return True
if __name__ == "__main__":
    init5()
    cycle.show_all()
    changeCycle()

    cycle.show_all()
