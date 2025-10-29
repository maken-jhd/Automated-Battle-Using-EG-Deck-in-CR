import time
import uiautomator2
from comCycle import CRCardCycle
from getCycle import init5
from changeCycle import changeCycle
from format2 import formatEG1x,formatEG2x,formatEG3x
import threading
import signal
import sys
from checkType import GameStateDetector

cycle = CRCardCycle()
d = uiautomator2.connect("127.0.0.1:16384")

class MainLoop:
    """主循环程序（增强版：支持线程间通信与协调）"""
    
    def __init__(self, device_id=None):
        self.device_id = device_id
        self.running = False
        self.game_detector = None
        self.op2_thread = None
        self.stop_op2_event = threading.Event()  # 用于通知操作2线程停止
        self.stop_op2_timeout = False
        
        # 设置信号处理，用于Ctrl+C中断
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理中断信号"""
        print(f"接收到信号 {signum}，正在停止程序...")
        self.running = False
        self.stop_op2_event.set()  # 通知操作2线程停止
        if self.game_detector:
            self.game_detector.stop_detection()
        if self.op2_thread and self.op2_thread.is_alive():
            self.op2_thread.join(timeout=2.0)  # 等待操作2线程结束
        sys.exit(0)
    
    def operation_1(self):
        """某操作1 - 在游戏开始前执行的操作"""
        print("执行操作1: 等待匹配或准备游戏...")
        print("5秒后退出游戏画面")
        time.sleep(5)
        d.click(750,2300)
        print("已退出游戏画面")
        time.sleep(5)
        print("回到主界面，3秒后开始匹配")
        for _ in range(50):
            d.click(1100,1500)
            time.sleep(0.03)
        d.click(750,2000)
        cycle.clear_all()
        print("已清空卡牌循环")
        time.sleep(1)  # 模拟操作耗时
    
    def operation_2(self, stop_event):
        """
        某操作2 - 在游戏开始后执行的操作
        
        Args:
            stop_event (threading.Event): 用于通知线程停止的事件
        """
        print("执行操作2: 游戏中的操作...")
        
        # 这里可以添加您的具体操作，例如：
        # - 放置卡牌
        # - 使用技能
        # - 其他游戏内操作
        
        # 模拟操作耗时，同时检查停止事件
        t0 = time.perf_counter()
        init5()
        cycle.show_all()
        if not changeCycle():
            print("线程2循环超时，自动跳出循环...")
            return
        cycle.show_all()
        #'''
        if stop_event.is_set():
            print("操作2线程收到停止信号，正在退出...")
            return
        for i in range(1,7):
            formatEG1x(6,1,i)
            if stop_event.is_set():
                print("操作2线程收到停止信号，正在退出...")
                return
        time.sleep(6)
        if stop_event.is_set():
            print("操作2线程收到停止信号，正在退出...")
            return
        time.sleep(6)
        if stop_event.is_set():
            print("操作2线程收到停止信号，正在退出...")
            return
        t1 = time.perf_counter()
        if t1 - t0 < 90:
            for i in range(1,7):
                formatEG1x(6,1,i)
                if stop_event.is_set():
                    print("操作2线程收到停止信号，正在退出...")
                    return
            time.sleep(5.5)
            if stop_event.is_set():
                print("操作2线程收到停止信号，正在退出...")
                return
            time.sleep(5.5)
            if stop_event.is_set():
                print("操作2线程收到停止信号，正在退出...")
                return
        else:
            #placeCardN("arrows",11)
            time.sleep(6)
            if stop_event.is_set():
                print("操作2线程收到停止信号，正在退出...")
                return
            time.sleep(6)
            if stop_event.is_set():
                print("操作2线程收到停止信号，正在退出...")
                return
        #'''
        #'''
        for i in range(4):
            time.sleep(2)
            if stop_event.is_set():
                print("操作2线程收到停止信号，正在退出...")
                return
            for j in range(1,8):
                formatEG2x(3,1,j)
                if stop_event.is_set():
                    print("操作2线程收到停止信号，正在退出...")
                    return
        #'''
        for i in range(3):
            for j in range(1,11):
                formatEG3x(2,1,j)
                if stop_event.is_set():
                    print("操作2线程收到停止信号，正在退出...")
                    return
        '''
        while not stop_event.is_set() and self.game_detector and self.game_detector.game_started:
            print("执行游戏内操作...")
            
            # 执行您的实际游戏操作
            # 例如: self.play_card(1)  # 放置第一张卡牌
            
            # 等待一段时间，但同时检查停止事件
            for _ in range(10):  # 将1秒分成10个0.1秒的间隔
                if stop_event.is_set():
                    print("操作2线程收到停止信号，正在退出...")
                    return
                time.sleep(0.1)
        '''
        print("操作2线程正常结束")
        self.stop_op2_timeout = True
    
    def run(self):
        """主循环"""
        self.running = True
        
        # 初始化游戏状态检测器
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "game_end_template.png")
        self.game_detector = GameStateDetector(
            device_id=self.device_id,
            #debug=True,
            debug=False,
            end_template_path=template_path
        )
        
        while self.running:
            print("\n=== 开始新一轮循环 ===")
            
            # 重置停止事件
            self.stop_op2_event.clear()
            self.stop_op2_timeout = False
            
            # 步骤1: 执行操作1
            self.operation_1()
            
            # 步骤2: 等待游戏开始
            print("等待游戏开始...")
            if self.game_detector.wait_for_game_start(timeout=30):
                print("游戏已开始!")
                
                # 启动游戏状态检测（双线程）
                self.game_detector.start_detection()
                
                # 创建并启动操作2线程
                self.op2_thread = threading.Thread(target=self.operation_2, args=(self.stop_op2_event,))
                self.op2_thread.daemon = True
                self.op2_thread.start()
                
                # 等待游戏结束
                print("等待游戏结束...")
                while self.running and not self.game_detector.game_ended and not self.stop_op2_timeout:
                    time.sleep(1)  # 每秒检查一次
                
                # 游戏结束，通知操作2线程停止
                print("游戏结束，通知操作2线程停止...")
                self.stop_op2_event.set()
                
                # 停止检测
                self.game_detector.stop_detection()
                
                # 等待操作2线程结束（最多等待5秒）
                if self.op2_thread and self.op2_thread.is_alive():
                    self.op2_thread.join(timeout=5.0)
                    if self.op2_thread.is_alive():
                        print("警告: 操作2线程未能在超时时间内结束")
                
                print("游戏结束，准备开始新一轮循环")
                
                # 重置游戏状态
                self.game_detector.game_started = False
                self.game_detector.game_ended = False
                
                # 短暂等待后再开始新一轮
                time.sleep(3)
            else:
                print("等待游戏开始超时，重新尝试...")
                time.sleep(2)  # 短暂等待后重试
        
        print("主循环结束")

# 使用示例
if __name__ == "__main__":
    # 创建主循环实例
    main_loop = MainLoop(device_id='127.0.0.1:16384')
    
    # 运行主循环
    try:
        main_loop.run()
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        main_loop.running = False

        main_loop.stop_op2_event.set()  # 确保操作2线程停止
