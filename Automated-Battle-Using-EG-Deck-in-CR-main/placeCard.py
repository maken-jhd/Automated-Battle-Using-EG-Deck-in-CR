import uiautomator2 as u2
from finalGetCards import CRCardRecognizer
import time
from comCycle import CRCardCycle
import config
d = u2.connect(config.DEVICE_ID)
cycle = CRCardCycle()
recognizer = CRCardRecognizer(config.DEVICE_ID)
cards_x = config.CARDS_X
cards_y = config.CARDS_Y
places_x = config.PLACES_X
places_y = config.PLACES_Y
def known(position):
    if cycle.get_card(position) == "Unknown":
        return False
    else:
        return True

def placeCardN(card_name,place_positon):
    global cards_x,cards_y,places_x,places_y
    tmp = cycle.find_card(card_name)
    tmp2 = tmp[0]
    card_position = tmp2['position']
    #print(card_position)
    d.click(cards_x[card_position - 1],cards_y[card_position - 1])
    d.click(places_x[place_positon],places_y[place_positon])
    cycle.use_card(card_position)
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