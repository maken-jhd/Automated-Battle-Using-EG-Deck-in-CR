import cv2
import numpy as np
import subprocess
import time
import os
import threading
from queue import Queue

class GameStateDetector:
    """游戏状态检测器（基于固定坐标）"""
    
    def __init__(self, device_id=None, debug=False, end_template_path=None):
        """
        初始化游戏状态检测器
        
        Args:
            device_id (str): 设备ID或地址，如 '127.0.0.1:16384'
            debug (bool): 是否启用调试模式，保存检测过程中的截图
            end_template_path (str): 游戏结束模板文件的绝对路径
        """
        self.device_id = device_id
        self.debug = debug
        self.debug_dir = "debug_game_state"
        self.end_template_path = end_template_path
        
        if debug:
            os.makedirs(self.debug_dir, exist_ok=True)
        
        # 游戏状态
        self.game_started = False
        self.game_ended = False
        
        # 线程控制
        self.running = False
        self.start_detection_thread = None
        self.end_detection_thread = None
        
        # 截图队列（用于线程间通信）
        self.screenshot_queue = Queue(maxsize=1)
        
        # 预加载结束模板（如果提供了路径）
        self.end_template = None
        if self.end_template_path and os.path.exists(self.end_template_path):
            self.end_template = cv2.imread(self.end_template_path)
            if self.end_template is None:
                print(f"错误: 无法加载模板文件: {self.end_template_path}")
            else:
                print(f"成功加载结束模板: {self.end_template_path}")
        elif self.end_template_path:
            print(f"警告: 模板文件不存在: {self.end_template_path}")
    
    def take_screenshot(self):
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
                print(f"ADB截图错误: {stderr.decode()}")
                return None
            
            # 将截图数据转换为numpy数组
            nparr = np.frombuffer(stdout, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return img
        except Exception as e:
            print(f"ADB截图异常: {e}")
            return None
    
    def detect_game_start(self, screenshot):
        """
        检测游戏是否开始（基于固定坐标的颜色检测）
        
        Args:
            screenshot: 游戏截图
            
        Returns:
            bool: 游戏是否开始
        """
        if screenshot is None:
            return False
        
        # 保存截图用于调试
        if self.debug:
            cv2.imwrite(os.path.join(self.debug_dir, f"detect_start_{int(time.time())}.png"), screenshot)
        
        # 提取指定区域 (280,2460) 到 (1400,2530)
        region = screenshot[2460:2530, 280:1400]
        
        # 保存区域截图用于调试
        if self.debug:
            cv2.imwrite(os.path.join(self.debug_dir, f"start_region_{int(time.time())}.png"), region)
        
        # 将BGR转换为RGB（因为OpenCV使用BGR，但颜色代码通常是RGB）
        region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        
        # 定义目标颜色 #C31EC9 (RGB)
        target_color = np.array([0xC3, 0x1E, 0xC9])
        
        # 计算与目标颜色的距离
        color_diff = np.abs(region_rgb - target_color)
        
        # 计算匹配的像素数量（允许一定的颜色偏差）
        match_mask = np.all(color_diff < [20, 20, 20], axis=2)
        match_count = np.count_nonzero(match_mask)
        total_pixels = region.shape[0] * region.shape[1]
        match_ratio = match_count / total_pixels
        
        # 调试输出
        if self.debug:
            print(f"开始检测 - 匹配像素比例: {match_ratio:.4f}")
        
        # 如果匹配比例超过阈值，则认为游戏已开始
        return match_ratio > 0.3
    
    def detect_game_end(self, screenshot):
        """
        检测游戏是否结束（基于固定坐标的模板匹配）
        
        Args:
            screenshot: 游戏截图
            
        Returns:
            bool: 游戏是否结束
        """
        if screenshot is None:
            return False
        
        # 如果没有加载模板，尝试加载
        if self.end_template is None:
            if self.end_template_path and os.path.exists(self.end_template_path):
                self.end_template = cv2.imread(self.end_template_path)
                if self.end_template is None:
                    print(f"错误: 无法加载模板文件: {self.end_template_path}")
                    return False
            else:
                print(f"警告: 模板文件不存在: {self.end_template_path}")
                return False
        
        # 保存截图用于调试
        if self.debug:
            cv2.imwrite(os.path.join(self.debug_dir, f"detect_end_{int(time.time())}.png"), screenshot)
        
        # 提取指定区域 (625,2200) 到 (800,2300)
        region = screenshot[2200:2300, 625:800]
        
        # 保存区域截图用于调试
        if self.debug:
            cv2.imwrite(os.path.join(self.debug_dir, f"end_region_{int(time.time())}.png"), region)
        
        # 调整模板大小以匹配区域大小（如果需要）
        if self.end_template.shape != region.shape:
            self.end_template = cv2.resize(self.end_template, (region.shape[1], region.shape[0]))
        
        # 使用模板匹配
        result = cv2.matchTemplate(region, self.end_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        
        # 调试输出
        if self.debug:
            print(f"结束检测 - 模板匹配得分: {max_val:.4f}")
        
        # 如果匹配得分超过阈值，则认为游戏已结束
        #print("结束匹配度：",max_val)
        return max_val > 0.5
    
    def start_detection_loop(self):
        """游戏开始检测循环（高频）"""
        print("开始检测线程启动")
        
        while self.running:
            # 获取截图
            screenshot = self.take_screenshot()
            
            # 将截图放入队列（供结束检测线程使用）
            if not self.screenshot_queue.full():
                self.screenshot_queue.put(screenshot)
            
            # 检测游戏开始
            if not self.game_started and self.detect_game_start(screenshot):
                self.game_started = True
                print(f"检测到游戏开始! (时间: {time.strftime('%Y-%m-%d %H:%M:%S')})")
            
            # 高频检测，间隔较短
            time.sleep(0.2)  # 每秒检测5次
        
        print("开始检测线程停止")
    
    def end_detection_loop(self):
        """游戏结束检测循环（低频）"""
        print("结束检测线程启动")
        
        while self.running:
            # 从队列获取截图（如果可用）
            screenshot = None
            if not self.screenshot_queue.empty():
                screenshot = self.screenshot_queue.get()
            
            # 如果队列中没有截图，自己获取一张
            if screenshot is None:
                screenshot = self.take_screenshot()
            
            # 检测游戏结束
            if self.game_started and not self.game_ended and self.detect_game_end(screenshot):
                self.game_ended = True
                print(f"检测到游戏结束! (时间: {time.strftime('%Y-%m-%d %H:%M:%S')})")
            
            # 低频检测，间隔较长
            time.sleep(2.0)  # 每2秒检测一次
        
        print("结束检测线程停止")
    
    def start_detection(self):
        """启动检测线程"""
        if self.running:
            print("检测已经在运行中")
            return
        
        self.running = True
        self.game_started = False
        self.game_ended = False
        
        # 启动开始检测线程（高频）
        self.start_detection_thread = threading.Thread(target=self.start_detection_loop)
        self.start_detection_thread.daemon = True
        self.start_detection_thread.start()
        
        # 启动结束检测线程（低频）
        self.end_detection_thread = threading.Thread(target=self.end_detection_loop)
        self.end_detection_thread.daemon = True
        self.end_detection_thread.start()
        
        print("游戏状态检测已启动")
    
    def stop_detection(self):
        """停止检测线程"""
        if not self.running:
            print("检测未在运行中")
            return
        
        self.running = False
        
        # 等待线程结束
        if self.start_detection_thread:
            self.start_detection_thread.join(timeout=1.0)
        
        if self.end_detection_thread:
            self.end_detection_thread.join(timeout=1.0)
        
        print("游戏状态检测已停止")
    
    def wait_for_game_start(self, timeout=30):
        """
        等待游戏开始
        
        Args:
            timeout (float): 超时时间（秒）
            
        Returns:
            bool: 是否成功检测到游戏开始
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            screenshot = self.take_screenshot()
            if self.detect_game_start(screenshot):
                self.game_started = True
                return True
            time.sleep(0.2)
        
        return False
    
    def wait_for_game_end(self, timeout=300):
        """
        等待游戏结束
        
        Args:
            timeout (float): 超时时间（秒）
            
        Returns:
            bool: 是否成功检测到游戏结束
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            screenshot = self.take_screenshot()
            if self.detect_game_end(screenshot):
                self.game_ended = True
                return True
            time.sleep(2.0)
        
        return False


# 使用示例
if __name__ == "__main__":
    # 创建游戏状态检测器，指定模板文件的绝对路径
    template_path = r"E:\codes\ClashRoyale\autoEgolem\templates\game_end_template.png"
    detector = GameStateDetector(
        device_id='127.0.0.1:16384',
        debug=True,
        end_template_path=template_path
    )
    
    # 方法1: 使用线程持续检测
    detector.start_detection()
    
    try:
        # 主线程可以执行其他操作
        while True:
            time.sleep(1.0)
            # 在这里执行您的游戏操作
            print("2")
            # ...
            
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        detector.stop_detection()
    
    # 方法2: 阻塞式等待
    # print("等待游戏开始...")
    # if detector.wait_for_game_start(timeout=30):
    #     print("游戏已开始!")
    #     
    #     print("等待游戏结束...")
    #     if detector.wait_for_game_end(timeout=300):
    #         print("游戏已结束!")
    #     else:
    #         print("等待游戏结束超时")
    # else:
    #     print("等待游戏开始超时")