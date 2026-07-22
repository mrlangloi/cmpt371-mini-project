from socket import *

serverPort = 12000

def start_tcp_server():
    # create TCP socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)
    print("The server is ready to receive")

while True:
    connectionSocket, addr = serverSocket.accept()
    print("Connection received from:", addr)

    request = connectionSocket.recv(1024).decode()
    print(request)
    # sentence = connectionSocket.recv(1024).decode()
    # capitalizedSentence = sentence.upper()

    # 304 - Not Modified; when user request has "If-Modified-Since"

    # 403 - Forbidden; when user request does not have permission to access

    # 404 - Not Found; when user request for something that does not exist

    # 505 - HTTP Version Not Supported; when user request is not HTTP1.1

    # 200 - OK; everything checks out correctly
    responseStatus = "HTTP/1.1 200 OK"
    connectionSocket.send(responseStatus.encode())
    # connectionSocket.send(capitalizedSentence.encode())

        connectionSocket.close()

if __name__ == "__main__":
    start_tcp_server()