class CRCardCycle:
    """皇室战争卡牌循环模拟器（单例模式）"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CRCardCycle, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, initial_available=None, initial_unavailable=None):
        # 防止重复初始化
        if CRCardCycle._initialized:
            return
            
        # 默认卡牌列表 - 全部设置为"Unknown"
        self.default_cards = ["Unknown"] * 8
        
        # 初始化可用和不可用卡牌队列
        if initial_available is not None:
            self.available = initial_available.copy()
        else:
            self.available = self.default_cards[:4]  # 前4张为可用卡牌
            
        if initial_unavailable is not None:
            self.unavailable = initial_unavailable.copy()
        else:
            self.unavailable = self.default_cards[4:]  # 后4张为不可用卡牌
            
        # 新增：置信度队列
        self.confidences_available = [0.0] * 4  # 可用队列的置信度
        self.confidences_unavailable = [0.0] * 4  # 不可用队列的置信度

        
        # 新增：卡牌池，包含所有可能的卡牌
        self.card_pool = ["archer", "arrows", "EGolem", "GRobot", "Ksk", "NWitch", "rage", "sk"]
        
        CRCardCycle._initialized = True
    
    def find_card(self, card_name, not_found_value=[]):
        """
        检索某张牌的位置
        
        Args:
            card_name (str): 要查找的卡牌名称
            not_found_value (any): 未找到卡牌时返回的值，默认为None
            
        Returns:
            list or any: 包含卡牌位置的列表，如果未找到则返回not_found_value
        """
        positions = []
        
        # 在可用队列中查找
        for i, card in enumerate(self.available):
            if card == card_name:
                positions.append({"type": "available", "position": i+1})
        
        # 在不可用队列中查找
        for i, card in enumerate(self.unavailable):
            if card == card_name:
                positions.append({"type": "unavailable", "position": i+5})
        
        # 如果未找到任何卡牌，返回特定值
        if not positions:
            return not_found_value
                
        return positions
    
    def use_card(self, position):
        """
        模拟使用一张卡牌
        
        Args:
            position (int): 要使用的卡牌位置（1-4）
            remove_from_cycle (bool): 是否将卡牌移出循环（不进入不可用队列）
            
        Returns:
            bool: 操作是否成功
        """
        if position < 1 or position > 4:
            print(f"错误：位置 {position} 无效，请输入1-4之间的数字")
            return False
            
        if len(self.available) < position:
            print(f"错误：位置 {position} 没有卡牌")
            return False
            
        # 获取要使用的卡牌及其置信度
        used_card = self.available[position-1]
        used_confidence = self.confidences_available[position-1]
        print(f"使用卡牌: 位置 {position} 的 {used_card} (置信度: {used_confidence:.2f})")

        # 将使用的卡牌和置信度移到不可用队列的末尾
        self.unavailable.append(used_card)
        self.confidences_unavailable.append(used_confidence)

        # 从不可用队列的开头取一张卡牌和置信度放到可用队列的相应位置
        if self.unavailable:
            new_card = self.unavailable.pop(0)
            new_confidence = self.confidences_unavailable.pop(0)
            self.available[position-1] = new_card
            self.confidences_available[position-1] = new_confidence
            print(f"新卡牌 {new_card} 进入位置 {position} (置信度: {new_confidence:.2f})")
        else:
            print("警告：不可用队列为空")
            
        return True
    
    def set_card(self, position, card_name, confidence=1.0, guess = False):
        """
        直接设置一张卡牌的位置，增强功能：
        1. 处理重复卡牌，保留置信度高的
        2. 置信度作为参数传入
        3. 如果设置后只剩一张Unknown卡牌，自动推断其身份
        
        Args:
            position (int): 要设置的位置（1-4为可用队列，5-8为不可用队列）
            card_name (str): 卡牌名称
            confidence (float): 卡牌置信度，默认为1.0
            
        Returns:
            bool: 操作是否成功
        """
        if position < 1 or position > 8:
            print(f"错误：位置 {position} 无效，请输入1-8之间的数字")
            return False
            
        # 记录设置前的卡牌状态
        old_unknown_count = self._count_unknown_cards()
            
        # 功能1: 检查重复卡牌并处理
        doLastGuess = False
        if card_name != "Unknown":
            existing_positions = self.find_card(card_name, [])
            for existing_pos in existing_positions:
                doLastGuess = True
                # 获取现有卡牌的置信度
                existing_confidence = self.get_confidence(existing_pos["type"], existing_pos["position"])
                
                # 比较置信度，保留置信度高的
                if confidence < existing_confidence:
                    print(f"卡牌 {card_name} 已存在于位置 {existing_pos['position']}，且置信度更高({existing_confidence:.2f} > {confidence:.2f})")
                    print(f"将位置 {position} 的卡牌设置为 Unknown")
                    result = self._set_card_internal(position, "Unknown", 0.0)
                    # 设置后检查是否需要推断Unknown卡牌
                    self._infer_unknown_card(old_unknown_count)
                    return result
                else:
                    print(f"卡牌 {card_name} 已存在于位置 {existing_pos['position']}，但当前设置置信度更高({confidence:.2f} > {existing_confidence:.2f})")
                    print(f"将位置 {existing_pos['position']} 的卡牌设置为 Unknown")
                    self._set_card_internal(
                        self._convert_position_to_internal(existing_pos["type"], existing_pos["position"]), 
                        "Unknown", 
                        0.0
                    )
        
        # 设置卡牌
        result = self._set_card_internal(position, card_name, confidence)
        
        # 设置后检查是否需要推断Unknown卡牌
        if doLastGuess or guess:
            self._infer_unknown_card(old_unknown_count)
        
        return result
    
    def _set_card_internal(self, position, card_name, confidence):
        """内部方法：实际设置卡牌位置和置信度"""
        if position <= 4:
            # 设置可用队列
            if len(self.available) < position:
                print(f"错误：可用队列位置 {position} 不存在")
                return False
                
            old_card = self.available[position-1]
            self.available[position-1] = card_name
            self.confidences_available[position-1] = confidence
            print(f"已将可用队列位置 {position} 的卡牌从 {old_card} 改为 {card_name} (置信度: {confidence:.2f})")
            return True
        else:
            # 设置不可用队列
            pos_in_unavailable = position - 5
            if len(self.unavailable) <= pos_in_unavailable:
                print(f"错误：不可用队列位置 {position} 不存在")
                return False
                
            old_card = self.unavailable[pos_in_unavailable]
            self.unavailable[pos_in_unavailable] = card_name
            self.confidences_unavailable[pos_in_unavailable] = confidence
            print(f"已将不可用队列位置 {position} 的卡牌从 {old_card} 改为 {card_name} (置信度: {confidence:.2f})")
            return True
    
    def _count_unknown_cards(self):
        """统计Unknown卡牌的数量"""
        count = 0
        
        # 统计可用队列中的Unknown
        count += sum(1 for card in self.available if card == "Unknown")
        
        # 统计不可用队列中的Unknown
        count += sum(1 for card in self.unavailable if card == "Unknown")
            
        return count
    
    def _infer_unknown_card(self, old_unknown_count):
        """
        推断Unknown卡牌的身份
        
        Args:
            old_unknown_count (int): 设置前的Unknown卡牌数量
        """
        # 获取当前的Unknown卡牌数量
        current_unknown_count = self._count_unknown_cards()
        
        # 如果Unknown卡牌数量从多个减少到1个，尝试推断
        #if old_unknown_count > 1 and current_unknown_count == 1:
        if current_unknown_count == 1:
            print("检测到只剩一张Unknown卡牌，尝试推断其身份...")
            
            # 获取所有已知卡牌
            known_cards = set()
            
            # 收集可用队列中的已知卡牌
            for card in self.available:
                if card != "Unknown":
                    known_cards.add(card)
            
            # 收集不可用队列中的已知卡牌
            for card in self.unavailable:
                if card != "Unknown":
                    known_cards.add(card)
            
            # 找出缺失的卡牌
            missing_card = None
            for card in self.card_pool:
                if card not in known_cards:
                    if missing_card is None:
                        missing_card = card
                    else:
                        # 如果找到多个缺失的卡牌，无法确定
                        missing_card = None
                        break
            
            # 如果确定缺失的卡牌，将其赋值给Unknown位置
            if missing_card is not None:
                print(f"推断出Unknown卡牌为: {missing_card}")
                
                # 找到Unknown卡牌的位置并设置
                for i, card in enumerate(self.available):
                    if card == "Unknown":
                        self._set_card_internal(i+1, missing_card, 1.0)
                        return
                
                for i, card in enumerate(self.unavailable):
                    if card == "Unknown":
                        self._set_card_internal(i+5, missing_card, 1.0)
                        return
    
    def _convert_position_to_internal(self, pos_type, position):
        """将位置描述转换为内部位置编号"""
        if pos_type == "available":
            return position
        elif pos_type == "unavailable":
            return position + 4  # 转换为5-8
        return position
    
    def get_confidence(self, pos_type, position):
        """获取指定位置的卡牌置信度"""
        if pos_type == "available" and 1 <= position <= 4:
            return self.confidences_available[position-1]
        elif pos_type == "unavailable" and 5 <= position <= 8:
            return self.confidences_unavailable[position-5]
        return 0.0
    
    def get_card(self, position):
        """
        获取指定位置的卡牌信息
        
        Args:
            position (int): 要获取的位置（1-4为可用队列，5-8为不可用队列）
            
        Returns:
            str: 卡牌名称，如果位置无效则返回None
        """
        if position < 1 or position > 8:
            print(f"错误：位置 {position} 无效，请输入1-8之间的数字")
            return None
            
        if position <= 4:
            if len(self.available) < position:
                print(f"错误：可用队列位置 {position} 不存在")
                return None
            return self.available[position-1]
        else:
            pos_in_unavailable = position - 5
            if len(self.unavailable) <= pos_in_unavailable:
                print(f"错误：不可用队列位置 {position} 不存在")
                return None
            return self.unavailable[pos_in_unavailable]
    
    def show_all(self):
        """显示所有卡牌的位置和置信度"""
        print("\n=== 当前卡牌状态 ===")
        print("可用队列:")
        for i, (card, confidence) in enumerate(zip(self.available, self.confidences_available)):
            print(f"  位置 {i+1}: {card} (置信度: {confidence:.2f})")
            
        print("\n不可用队列:")
        for i, (card, confidence) in enumerate(zip(self.unavailable, self.confidences_unavailable)):
            print(f"  位置 {i+5}: {card} (置信度: {confidence:.2f})")
        print("==================\n")
    
    def get_cycle_state(self):
        """
        获取当前循环状态（可用于保存状态）
        
        Returns:
            dict: 包含可用和不可用队列的字典
        """
        return {
            "available": self.available.copy(),
            "unavailable": self.unavailable.copy(),
            "confidences_available": self.confidences_available.copy(),
            "confidences_unavailable": self.confidences_unavailable.copy(),
        }
    
    def set_cycle_state(self, state):
        """
        设置循环状态（可用于恢复状态）
        
        Args:
            state (dict): 包含可用和不可用队列的字典
            
        Returns:
            bool: 操作是否成功
        """
        if "available" in state and "unavailable" in state:
            self.available = state["available"].copy()
            self.unavailable = state["unavailable"].copy()
            
            # 恢复置信度队列
            if "confidences_available" in state:
                self.confidences_available = state["confidences_available"].copy()
            if "confidences_unavailable" in state:
                self.confidences_unavailable = state["confidences_unavailable"].copy()

                
            print("已恢复卡牌循环状态")
            return True
        else:
            print("错误：无效的状态格式")
            return False
    def clear_all(self,initial_available=None, initial_unavailable=None):
        # 初始化可用和不可用卡牌队列
        if initial_available is not None:
            self.available = initial_available.copy()
        else:
            self.available = self.default_cards[:4]  # 前4张为可用卡牌
            
        if initial_unavailable is not None:
            self.unavailable = initial_unavailable.copy()
        else:
            self.unavailable = self.default_cards[4:]  # 后4张为不可用卡牌
            
        # 新增：置信度队列
        self.confidences_available = [0.0] * 4  # 可用队列的置信度
        self.confidences_unavailable = [0.0] * 4  # 不可用队列的置信度


# 示例使用
if __name__ == "__main__":
    # 创建卡牌循环模拟器
    cycle = CRCardCycle()
    
    # 显示初始状态
    cycle.show_all()
    
    # 设置一些卡牌（带置信度）
    cycle.set_card(1, "archer", 0.85)
    cycle.set_card(2, "arrows", 0.90)
    cycle.set_card(3, "EGolem", 0.78)
    cycle.set_card(4, "GRobot", 0.92)
    cycle.set_card(5, "Ksk", 0.82)
    cycle.set_card(6, "NWitch", 0.88)
    cycle.set_card(7, "rage", 0.75)
    # 故意不设置位置8，让它保持Unknown
    
    # 显示当前状态（应该有7张已知卡牌和1张Unknown卡牌）
    cycle.show_all()
    
    # 现在设置一张重复卡牌，触发置信度比较
    # 这将导致一张卡牌被设置为Unknown，但随后会自动推断出Unknown卡牌的身份
    cycle.set_card(8, "archer", 0.70)  # 设置一个低置信度的重复卡牌
    
    # 显示最终状态（所有卡牌都应该已知）
    cycle.show_all()