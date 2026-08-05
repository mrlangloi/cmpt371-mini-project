from socket import *
import threading

serverPort = 12001

def handle_proxy_request(clientSocket):
    # receive client request
    requestData = clientSocket.recv(1024).decode()

    if not requestData:
        return

    clientSocket.setBlocking(False)

    print("Request Data:")
    print(requestData)

    # parse the request
    headers = requestData.split('\r\n')
    firstHeader = headers[0].split(' ')
    method, url, version = firstHeader
    print(f"Method: {method}, URL: {url}, Version: {version}")
    

def start_tcp_proxy():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(4)
    print("The proxy is ready to receive")

    while True:
        connectionSocket, addr = serverSocket.accept()
        print("Connection received from:", addr)

        # process the request
        clientHandler = threading.Thread(target=handle_proxy_request, args=(connectionSocket,))
        clientHandler.start()

        connectionSocket.close()

if __name__ == "__main__":
    start_tcp_proxy()