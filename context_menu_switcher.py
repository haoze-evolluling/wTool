import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import ctypes
import sys
import subprocess
import os
import time


def run_as_admin():
    try:
        if sys.platform == 'win32':
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            return True
    except Exception as e:
        print(f"Error running as admin: {e}")
    return False


class ContextMenuSwitcher:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("Windows系统工具箱")
            self.root.geometry("650x580")
            self.root.resizable(False, False)
            
            self.current_mode = self.get_current_mode()
            
            self.setup_ui()
            
            self.root.update()
            self.root.after(500, self.check_admin_privileges)
        except Exception as e:
            messagebox.showerror("初始化错误", f"程序初始化时出错：{str(e)}")
            sys.exit(1)
        
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=("Microsoft YaHei UI", 18, "bold"), foreground="#2c3e50")
        style.configure('Status.TLabel', font=("Microsoft YaHei UI", 11))
        style.configure('Info.TLabel', font=("Microsoft YaHei UI", 9))
        
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(
            main_frame,
            text="Windows系统工具箱",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 25))
        
        info_frame = ttk.LabelFrame(main_frame, text="当前状态", padding="15")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = ttk.Label(
            info_frame,
            text=f"右键菜单模式: {self.current_mode}",
            style='Status.TLabel'
        )
        self.status_label.pack(anchor=tk.W, pady=2)
        
        mode_frame = ttk.LabelFrame(main_frame, text="右键菜单切换", padding="15")
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.mode_var = tk.StringVar(value=self.current_mode)
        
        win10_radio = ttk.Radiobutton(
            mode_frame,
            text="Windows 10 右键菜单（经典样式）",
            variable=self.mode_var,
            value="Windows 10",
            command=self.on_mode_change
        )
        win10_radio.pack(anchor=tk.W, pady=6)
        
        win11_radio = ttk.Radiobutton(
            mode_frame,
            text="Windows 11 右键菜单（现代样式）",
            variable=self.mode_var,
            value="Windows 11",
            command=self.on_mode_change
        )
        win11_radio.pack(anchor=tk.W, pady=6)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.switch_button = ttk.Button(
            button_frame,
            text="应用更改",
            command=self.apply_changes
        )
        self.switch_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        restart_button = ttk.Button(
            button_frame,
            text="重启文件资源管理器",
            command=self.restart_explorer
        )
        restart_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        
        dns_frame = ttk.LabelFrame(main_frame, text="网络工具", padding="15")
        dns_frame.pack(fill=tk.X, pady=(0, 15))
        
        dns_info_label = ttk.Label(
            dns_frame,
            text="清理本地DNS缓存可以解决网络连接问题",
            style='Info.TLabel',
            foreground="#666"
        )
        dns_info_label.pack(anchor=tk.W, pady=(0, 10))
        
        dns_button = ttk.Button(
            dns_frame,
            text="清理DNS缓存",
            command=self.clear_dns_cache
        )
        dns_button.pack(fill=tk.X)
        
        admin_frame = ttk.LabelFrame(main_frame, text="权限信息", padding="12")
        admin_frame.pack(fill=tk.X)
        
        self.admin_label = ttk.Label(
            admin_frame,
            text="检查管理员权限中...",
            style='Info.TLabel'
        )
        self.admin_label.pack(anchor=tk.W)
        
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def check_admin_privileges(self):
        try:
            if self.is_admin():
                self.admin_label.config(
                    text="✓ 已获得管理员权限",
                    foreground="#27ae60"
                )
            else:
                self.admin_label.config(
                    text="✗ 未获得管理员权限",
                    foreground="#e74c3c"
                )
                result = messagebox.askyesno(
                    "权限提示",
                    "程序需要管理员权限才能使用完整功能。\n\n是否自动以管理员身份重新启动程序？"
                )
                if result:
                    self.root.destroy()
                    run_as_admin()
                    sys.exit(0)
                else:
                    messagebox.showwarning(
                        "权限警告",
                        "部分功能可能无法正常使用。\n建议以管理员身份运行此程序。"
                    )
        except Exception as e:
            self.admin_label.config(
                text="权限检测失败",
                foreground="#e74c3c"
            )
    
    def get_current_mode(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            )
            winreg.CloseKey(key)
            return "Windows 10"
        except WindowsError:
            return "Windows 11"
        except Exception as e:
            print(f"Error getting current mode: {e}")
            return "Windows 11"
    
    def on_mode_change(self):
        selected_mode = self.mode_var.get()
        if selected_mode != self.current_mode:
            self.switch_button.config(state=tk.NORMAL)
        else:
            self.switch_button.config(state=tk.DISABLED)
    
    def apply_changes(self):
        if not self.is_admin():
            messagebox.showerror(
                "权限错误",
                "需要管理员权限才能应用更改！\n请以管理员身份运行此程序。"
            )
            return
        
        selected_mode = self.mode_var.get()
        
        try:
            if selected_mode == "Windows 10":
                self.enable_win10_menu()
            else:
                self.enable_win11_menu()
            
            self.current_mode = selected_mode
            self.status_label.config(text=f"当前模式: {self.current_mode}")
            self.switch_button.config(state=tk.DISABLED)
            
            result = messagebox.askyesno(
                "应用成功",
                f"已成功切换到 {selected_mode} 右键菜单！\n\n是否立即重启文件资源管理器以应用更改？"
            )
            
            if result:
                self.restart_explorer()
            
        except Exception as e:
            messagebox.showerror(
                "错误",
                f"应用更改时出错：{str(e)}"
            )
    
    def enable_win10_menu(self):
        key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
        except WindowsError:
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                key_path
            )
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
    
    def enable_win11_menu(self):
        key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
        
        try:
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                key_path + r"\InprocServer32"
            )
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                key_path
            )
        except WindowsError:
            pass
    
    def restart_explorer(self):
        try:
            subprocess.run(
                ["taskkill", "/f", "/im", "explorer.exe"],
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            subprocess.Popen("explorer.exe")
            messagebox.showinfo(
                "重启成功",
                "文件资源管理器已成功重启！"
            )
        except Exception as e:
            messagebox.showerror(
                "错误",
                f"重启文件资源管理器时出错：{str(e)}"
            )
    
    def clear_dns_cache(self):
        if not self.is_admin():
            messagebox.showerror(
                "权限错误",
                "需要管理员权限才能清理DNS缓存！\n请以管理员身份运行此程序。"
            )
            return
        
        try:
            result = messagebox.askyesno(
                "确认清理",
                "确定要清理本地DNS缓存吗？\n\n这可能会暂时影响网络连接。"
            )
            
            if result:
                process = subprocess.Popen(
                    ["ipconfig", "/flushdns"],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                output, error = process.communicate()
                
                if process.returncode == 0:
                    messagebox.showinfo(
                        "清理成功",
                        "DNS缓存已成功清理！\n\n网络连接可能需要几秒钟恢复正常。"
                    )
                else:
                    messagebox.showerror(
                        "清理失败",
                        f"清理DNS缓存时出错：\n{error}"
                    )
        except Exception as e:
            messagebox.showerror(
                "错误",
                f"清理DNS缓存时出错：{str(e)}"
            )


def main():
    try:
        root = tk.Tk()
        app = ContextMenuSwitcher(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("程序错误", f"程序运行时发生错误：{str(e)}\n\n请检查是否已安装Python 3.6或更高版本。")
        print(f"Main error: {e}")


if __name__ == "__main__":
    main()
