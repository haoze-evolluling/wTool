import subprocess
import threading
import time


class ShutdownScheduler:
    def __init__(self):
        self.shutdown_timer = None
        self.is_shutdown_scheduled = False
        self.cancel_event = threading.Event()
        self.shutdown_type = None
        self.target_time_str = ""
        self.remaining_seconds = 0
    
    def schedule_countdown_shutdown(self, seconds, callback=None):
        """
        倒计时关机
        :param seconds: 倒计时秒数
        :param callback: 回调函数
        :return: 是否成功
        """
        if self.is_shutdown_scheduled:
            return False, "已有关机计划，请先取消"
        
        self.cancel_event.clear()
        self.is_shutdown_scheduled = True
        self.shutdown_type = "countdown"
        self.remaining_seconds = seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            self.target_time_str = f"{hours}小时{minutes}分钟{secs}秒后关机"
        elif minutes > 0:
            self.target_time_str = f"{minutes}分钟{secs}秒后关机"
        else:
            self.target_time_str = f"{secs}秒后关机"
        
        def countdown_thread():
            remaining = seconds
            while remaining > 0 and not self.cancel_event.is_set():
                time.sleep(1)
                remaining -= 1
                self.remaining_seconds = remaining
                if callback and remaining % 10 == 0:
                    callback(remaining)
            
            if not self.cancel_event.is_set():
                self.execute_shutdown()
            else:
                self.is_shutdown_scheduled = False
        
        self.shutdown_timer = threading.Thread(target=countdown_thread, daemon=True)
        self.shutdown_timer.start()
        
        return True, f"已设置 {seconds} 秒后关机"
    
    def schedule_fixed_time_shutdown(self, target_time, callback=None):
        """
        固定时间关机
        :param target_time: 目标时间，格式为 "HH:MM"
        :param callback: 回调函数
        :return: 是否成功
        """
        if self.is_shutdown_scheduled:
            return False, "已有关机计划，请先取消"
        
        try:
            import datetime
            now = datetime.datetime.now()
            target_hour, target_minute = map(int, target_time.split(':'))
            
            target_datetime = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            
            if target_datetime <= now:
                target_datetime += datetime.timedelta(days=1)
            
            seconds = int((target_datetime - now).total_seconds())
            
            self.cancel_event.clear()
            self.is_shutdown_scheduled = True
            self.shutdown_type = "fixed"
            self.remaining_seconds = seconds
            self.target_time_str = f"将在 {target_time} 关机"
            
            def fixed_time_thread():
                remaining = seconds
                while remaining > 0 and not self.cancel_event.is_set():
                    time.sleep(1)
                    remaining -= 1
                    self.remaining_seconds = remaining
                    if callback and remaining % 60 == 0:
                        callback(remaining)
                
                if not self.cancel_event.is_set():
                    self.execute_shutdown()
                else:
                    self.is_shutdown_scheduled = False
            
            self.shutdown_timer = threading.Thread(target=fixed_time_thread, daemon=True)
            self.shutdown_timer.start()
            
            return True, f"已设置在 {target_time} 关机"
        
        except Exception as e:
            return False, f"时间格式错误：{str(e)}"
    
    def cancel_shutdown(self):
        """
        取消关机计划
        :return: 是否成功
        """
        if not self.is_shutdown_scheduled:
            return False, "没有活动的关机计划"
        
        self.cancel_event.set()
        self.is_shutdown_scheduled = False
        
        return True, "已取消关机计划"
    
    def execute_shutdown(self):
        """
        执行关机
        """
        try:
            subprocess.run(["shutdown", "/s", "/t", "0"], shell=True, check=True)
        except Exception as e:
            print(f"关机失败：{e}")
    
    def get_remaining_time(self):
        """
        获取剩余时间（秒）
        :return: 剩余秒数，如果没有计划则返回0
        """
        if not self.is_shutdown_scheduled:
            return 0
        return -1  # 无法精确获取剩余时间
    
    def is_scheduled(self):
        """
        是否有关机计划
        :return: 是否有计划
        """
        return self.is_shutdown_scheduled
    
    def get_status(self):
        """
        获取关机状态
        :return: 状态字符串
        """
        if not self.is_shutdown_scheduled:
            return "未设置定时关机"
        
        if self.shutdown_type == "countdown":
            hours = self.remaining_seconds // 3600
            minutes = (self.remaining_seconds % 3600) // 60
            secs = self.remaining_seconds % 60
            if hours > 0:
                return f"{hours}小时{minutes}分钟{secs}秒后关机"
            elif minutes > 0:
                return f"{minutes}分钟{secs}秒后关机"
            else:
                return f"{secs}秒后关机"
        else:
            return self.target_time_str


if __name__ == "__main__":
    scheduler = ShutdownScheduler()
    
    def countdown_callback(seconds):
        print(f"剩余时间：{seconds} 秒")
    
    print("测试倒计时关机（10秒）")
    success, message = scheduler.schedule_countdown_shutdown(10, countdown_callback)
    print(message)
    
    time.sleep(5)
    print("\n取消关机")
    success, message = scheduler.cancel_shutdown()
    print(message)
    
    print("\n测试固定时间关机")
    import datetime
    target = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime("%H:%M")
    success, message = scheduler.schedule_fixed_time_shutdown(target, countdown_callback)
    print(message)
    
    time.sleep(5)
    print("\n取消关机")
    success, message = scheduler.cancel_shutdown()
    print(message)
