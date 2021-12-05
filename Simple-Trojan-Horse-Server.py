import socket
import time
import threading


class ClientThread(threading.Thread):
    def __init__(self, serverSocket, clientSocket, clientAddress, clientSocketsList, clientIndex):
        threading.Thread.__init__(self)
        self.serverSocket = serverSocket
        self.clientSocket = clientSocket
        self.clientAddress = clientAddress
        self.clientSocketsList = clientSocketsList
        self.clientIndex = clientIndex
        self.counter = 0

    def run(self):
        self.clientSocketsList.append(self.clientSocket)

        clientIndexString = str(self.clientIndex)
        self.clientSocket.sendall(clientIndexString.encode())

        # Catch clients message
        while True:
            if getattr(self.serverSocket, '_closed') == False and getattr(self.clientSocket, '_closed') == False:
                try:
                    clientMessage = str(self.clientSocket.recv(1024), encoding='utf8')

                    counter = 0

                except:
                    if counter < 3:
                        print("Socket Error: Receiving client " + str(self.clientIndex) + " message failed.")
                        print("Try to receive client " + str(self.clientIndex) + " message again in 3 sec.")

                        counter += 1

                        time.sleep(3)
                    else:
                        print("Socket Error: Receiving client " + str(self.clientIndex) + " message failed.")
                        break

                if clientMessage == 'client stop':
                    break
                elif clientMessage != None:
                    print(clientMessage)
            else:
                break

        self.clientSocketsList.remove(self.clientSocket)
        self.clientSocket.close()
        print('Status: client ' + str(self.clientIndex) + ' is stopped.')


class ServerThread(threading.Thread):
    def __init__(self, serverSocket, clientSocketsList, threadsList):
        threading.Thread.__init__(self)
        self.serverSocket = serverSocket
        self.clientSocketsList = clientSocketsList
        self.threadsList = threadsList
        self.clientIndex = 0
        self.counter = 0

    def run(self):
        while getattr(self.serverSocket, '_closed') == False:
            print('Status: Waiting for new client connection...')

            try:
                clientSocket, clientAddress = self.serverSocket.accept()
            except:
                break

            clientsThread = ClientThread(serverSocket=self.serverSocket, clientSocket=clientSocket, clientAddress=clientAddress, clientSocketsList=self.clientSocketsList, clientIndex=self.clientIndex)
            self.threadsList.append(clientsThread)

            try:
                clientsThread.start()

                self.counter = 0
            except:
                if self.counter < 3:
                    print("Thread Error: Client thread created failed.")
                    print("Message: Try to create client thread again in 3 sed.")

                    self.counter += 1

                    time.sleep(3)
                else:
                    print("Client thread created failed.")
                    exit()

            self.clientIndex += 1

        for i in range(1, len(self.threadsList)):
            self.threadsList[i].join()

        print('Status: Server is stopped.')


def main():
    # Set server IP and port
    hostIP = '127.0.0.1'
    port = 48763
    counter = 0

    # Launch server socket
    while True:
        try:
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.bind((hostIP, port))
            serverSocket.listen(4)

            print('Status: Server is launched.')

            counter = 0

            break
        except:
            if counter < 3:
                print("Socket Error: Server launched failed.")
                print("Message: Try to launch server again in 3 sec.")

                counter += 1

                time.sleep(3)
            else:
                print("Server launched failed.")
                exit()

    # Declare two lists which are used to store client sockets and threads
    clientSocketsList = []
    threadsList = []

    # Create server thread to process accepting client sockets task
    serverThread = ServerThread(serverSocket=serverSocket, clientSocketsList=clientSocketsList, threadsList=threadsList)
    threadsList.append(serverThread)

    try:
        serverThread.start()

        counter = 0
    except:
        if counter < 3:
            print("Thread Errror: Server thread created failed.")
            print("Message: Try to create server thread again in 3 sec.")

            counter += 1

            time.sleep(3)
        else:
            print("Server thread created failed.")
            exit()

    # Catch commands
    while True:
        lineUnsplit = str(input())
        lineSplit = lineUnsplit.split(' ')

        # command = server stop
        if len(lineSplit) == 2:
            if lineSplit[0] == 'server' and lineSplit[1] == 'stop':
                for clientSocket in clientSocketsList:
                    stopMessage = 'stop'

                    while True:
                        try:
                            clientSocket.sendall(stopMessage.encode())

                            counter = 0

                            break
                        except:
                            if counter < 3:
                                print("Socket Error: Sending stop message failed.")
                                print("Message: Try to send stop message again in 3 sec.")

                                counter += 1

                                time.sleep(3)
                            else:
                                print("Sending stop message failed.")
                                exit()
                    
                break

        # command is incomplete
        if len(lineSplit) < 3:
            print("Format Error: Too few parameters.")
            continue

        # Combine command
        for i in range(len(lineSplit) - 3):
            lineSplit[2] += (" " + lineSplit[3])
            del lineSplit[3]

        try:
            clientIndex = int(lineSplit[1])

            while True:
                try:
                    clientSocketsList[clientIndex].sendall(lineSplit[2].encode())

                    counter = 0

                    break
                except:
                    if counter < 3:
                        print("Socket Error: Sending command failed.")
                        print("Message: Try to send command again in 3 sec.")
                        time.sleep(3)
                    else:
                        print("Sending command failed.")
                        exit()
        except:
            print("Format Error: Client index is not a integer.")

    serverSocket.close()

    threadsList[0].join()


if __name__ == '__main__':
    main()