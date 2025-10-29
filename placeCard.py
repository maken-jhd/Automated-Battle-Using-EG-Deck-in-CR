import uiautomator2 as u2
from finalGetCards import CRCardRecognizer
import time
from comCycle import CRCardCycle
d = u2.connect('127.0.0.1:16384')
cycle = CRCardCycle()
recognizer = CRCardRecognizer('127.0.0.1:16384')
cards_x = [455,720,975,1250]
cards_y = [2273,2450,2273,2273]
places_x = [680,754,154,1304,680,754,680,754,346,1085,520,900]
places_y = [1926,1926,1890,1890,1487,1487,1158,1158,1164,1164,725,725]
def known(position):
    if cycle.get_card(position) == "Unknown":
        return False
    else:
        return True

def placeCardN(card_name,place_positon,remove=False):
    global cards_x,cards_y,places_x,places_y
    tmp = cycle.find_card(card_name)
    tmp2 = tmp[0]
    card_position = tmp2['position']
    #print(card_position)
    d.click(cards_x[card_position - 1],cards_y[card_position - 1])
    d.click(places_x[place_positon],places_y[place_positon])
    cycle.use_card(card_position,remove)
    if not known(card_position):
        time.sleep(1.5)
        tmpCard = recognizer.get_card_at_position(card_position)
        cycle.set_card(card_position,tmpCard["name"],tmpCard["confidence"])

def placeCardP(card_position,place_positon):
    global cards_x,cards_y,places_x,places_y
    d.click(cards_x[card_position - 1],cards_y[card_position - 1])
    d.click(places_x[place_positon],places_y[place_positon])
    cycle.use_card(card_position)
    if not known(card_position):
        time.sleep(1.5)
        tmpCard = recognizer.get_card_at_position(card_position)
        cycle.set_card(card_position,tmpCard["name"],tmpCard["confidence"])


#["archer", "arrows", "EGolem", "GRobot", "Ksk", "NWitch", "rage", "sk"]
if __name__ == "__main__":
    '''
    cycle.set_card(1, "EGolem")
    cycle.set_card(2, "archer")
    cycle.set_card(3, "Ksk")
    cycle.set_card(4, "arrows")
    cycle.set_card(5,"GRobot")
    cycle.show_all()
    placeCardN("EGolem",0)
    placeCardN("arrows",4)
    time.sleep(2)
    placeCardN("GRobot",8)
    '''
    placeCardP(2,4)