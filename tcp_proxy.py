from socket import *

serverPort = 12001

def start_tcp_proxy():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(4)
    print("The proxy is ready to receive")

    while True:
        connectionSocket, addr = serverSocket.accept()
        print("Connection received from:", addr)

        connectionSocket.close()

if __name__ == "__main__":
    start_tcp_proxy()