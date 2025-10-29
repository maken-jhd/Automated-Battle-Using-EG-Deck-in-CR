from finalGetCards import CRCardRecognizer
from comCycle import CRCardCycle
from placeCard import placeCardP
import time
import config

# 创建识别器和卡牌循环的实例
recognizer = CRCardRecognizer(config.DEVICE_ID)
cycle = CRCardCycle()  # 创建CRCardCycle的实例

def init5():
    firstcards = recognizer.get_all_cards()
    for card in firstcards:
        # [{position,name,confidence}]
        
        if card['position'] != "next":
            # 使用实例调用set_card方法
            cycle.set_card(card['position'], str(card['name']),card['confidence'])
        else:
            if card['name'] == "Unknown" or card['confidence'] < 0.3:
                continue
            else:
                # 设置不可用队列的第一张牌
                cycle.set_card(5, card['name'],card['confidence'])
                # 注意：这里只设置了第一张不可用牌，您可能需要设置所有4张不可用牌
                # 如果您有其他不可用牌的信息，需要相应地设置位置6、7、8
def test(x,px):
    #x = 1
    #px = 0
    placeCardP(x,px)
    time.sleep(2)
    cycle.set_card(x,recognizer.get_card_at_position(x)['name'],recognizer.get_card_at_position(x)['confidence'])

if __name__ == "__main__":
    init5()
    cycle.show_all()  # 使用实例调用show_all方法，并添加括号
    test(1,0)
    test(3,8)
    test(2,4)
    test(4,6)
    cycle.show_all()