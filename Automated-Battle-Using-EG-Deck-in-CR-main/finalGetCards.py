import cv2
import numpy as np
import uiautomator2 as u2
import time
import subprocess
import os
import config

class CRCardRecognizer:
    """皇室战争卡牌识别器"""
    
    def __init__(self, device_id=None):
        """
        初始化卡牌识别器
        
        Args:
            device_id (str, optional): 设备ID或地址，如 '127.0.0.1:16384'. 默认为None，连接默认设备
        """
        try:
            # 获取当前脚本所在目录
            self.script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 创建必要的子目录
            self.cards_dir = os.path.join(self.script_dir, "cards")
            os.makedirs(self.cards_dir, exist_ok=True)
            
            # 建立连接
            if device_id:
                self.d = u2.connect(device_id)
                self.device_id = device_id
            else:
                self.d = u2.connect()
                self.device_id = None
            
            # 获取屏幕尺寸
            self.width, self.height = self.d.window_size()
            
            self.setup_regions()
            self.load_templates()
            
        except Exception as e:
            print(f"初始化卡牌识别器时发生错误: {e}")
            self.d = None

    def setup_regions(self):
        """设置卡牌区域坐标"""
        self.card_regions = config.CARD_REGIONS
        self.next_card_region = config.NEXT_CARD_REGION

    def load_templates(self):
        """加载卡牌模板"""
        self.templates = {}
        card_names = ["archer", "arrows", "EGolem", "GRobot", "Ksk", "NWitch", "rage", "sk"]
        
        for name in card_names:
            template_path = os.path.join(self.cards_dir, f"{name}.png")
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is not None:
                self.templates[name] = template

    def ensure_game_foreground(self):
        """确保游戏处于前台"""
        current_app = self.d.app_current()
        
        if current_app['package'] != 'com.tencent.tmgp.supercell.clashroyale':
            # 启动游戏
            self.d.app_start('com.tencent.tmgp.supercell.clashroyale')
            time.sleep(5)  # 等待游戏加载
            
            # 再次检查
            current_app = self.d.app_current()
            if current_app['package'] == 'com.tencent.tmgp.supercell.clashroyale':
                return True
            else:
                return False
        return True
    
    def adb_screenshot(self):
        """使用ADB命令截图"""
        try:
            # 确定ADB命令
            if self.device_id:
                adb_cmd = f"adb -s {self.device_id} exec-out screencap -p"
            else:
                adb_cmd = "adb exec-out screencap -p"
            
            # 执行ADB截图命令
            process = subprocess.Popen(adb_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if stderr:
                return None
            
            # 将截图数据转换为numpy数组
            nparr = np.frombuffer(stdout, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return img
        except Exception:
            return None

    def recognize_card(self, region):
        """识别单个卡牌"""
        if self.d is None:
            return "Device Not Connected", 0.0
        
        # 确保游戏在前台
        if not self.ensure_game_foreground():
            return "Game Not Foreground", 0.0
        
        # 获取截图
        screenshot = self.adb_screenshot()
        if screenshot is None:
            return "Screenshot Failed", 0.0
        
        # 检查区域坐标
        x, y, w, h = region
        
        # 检查区域是否在截图范围内
        if x >= screenshot.shape[1] or y >= screenshot.shape[0]:
            return "Region Out of Bounds", 0.0
            
        if x + w > screenshot.shape[1] or y + h > screenshot.shape[0]:
            return "Region Out of Bounds", 0.0
        
        # 截取卡牌区域
        card_img = screenshot[y:y+h, x:x+w]
        
        # 检查截取的区域是否为空
        if card_img is None or card_img.size == 0:
            return "Empty Card Image", 0.0
        
        # 模板匹配
        best_match = None
        best_score = 0
        
        # 与所有模板进行匹配
        for name, template in self.templates.items():
            # 调整模板大小以匹配卡牌区域
            resized_template = cv2.resize(template, (w, h))
            
            # 使用模板匹配
            result = cv2.matchTemplate(card_img, resized_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > best_score:
                best_score = max_val
                best_match = name
        
        # 设置匹配阈值为0.3
        if best_score > 0.05:
            return best_match, best_score
        else:
            return "Unknown", best_score

    def get_all_cards(self):
        """
        获取所有卡牌信息
        
        Returns:
            list: 包含所有卡牌信息的列表，每个元素是一个字典，包含位置、名称和置信度
        """
        results = []
        
        # 识别4张当前卡牌
        for i, region in enumerate(self.card_regions):
            card_name, confidence = self.recognize_card(region)
            results.append({
                "position": i+1,
                "name": card_name,
                "confidence": confidence
            })
        
        # 识别下一张卡牌
        next_card, next_confidence = self.recognize_card(self.next_card_region)
        results.append({
            "position": "next",
            "name": next_card,
            "confidence": next_confidence
        })
        
        return results

    def get_card_at_position(self, position):
        """
        获取指定位置的卡牌信息
        
        Args:
            position (int or str): 卡牌位置，1-4表示当前卡牌，"next"表示下一张卡牌
            
        Returns:
            dict: 卡牌信息，包含位置、名称和置信度
        """
        if isinstance(position, int) and 1 <= position <= 4:
            region = self.card_regions[position-1]
            card_name, confidence = self.recognize_card(region)
            return {
                "position": position,
                "name": card_name,
                "confidence": confidence
            }
        elif position == "next":
            card_name, confidence = self.recognize_card(self.next_card_region)
            return {
                "position": "next",
                "name": card_name,
                "confidence": confidence
            }
        else:
            return {
                "position": position,
                "name": "Invalid Position",
                "confidence": 0.0
            }

# 外部调用示例
if __name__ == "__main__":
    # 创建识别器实例，连接到指定设备
    recognizer = CRCardRecognizer(config.DEVICE_ID)
    
    # 检查连接是否成功
    if recognizer.d is not None:
        # 等待一段时间确保游戏界面完全加载
        time.sleep(2)
        
        # 方法1: 获取所有卡牌信息
        all_cards = recognizer.get_all_cards()
        print("所有卡牌信息:")
        for card in all_cards:
            print(f"位置 {card['position']}: {card['name']} (置信度: {card['confidence']:.2f})")
        
        print("\n")
        
        # 方法2: 获取特定位置的卡牌信息
        card_1 = recognizer.get_card_at_position(1)
        print(f"第一张卡牌: {card_1['name']} (置信度: {card_1['confidence']:.2f})")
        
        next_card = recognizer.get_card_at_position("next")
        print(f"下一张卡牌: {next_card['name']} (置信度: {next_card['confidence']:.2f})")
    else:
        print("无法进行识别，因为设备连接失败")