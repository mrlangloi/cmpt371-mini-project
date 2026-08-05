from socket import *
import threading

serverPort = 12001

# e.g., b"GET /api/v1 HTTP/1.1\r\nHost: localhost:8080\r\nAccept: */*\r\n\r\n"
# returns ('localhost', 8080)
def get_host_port(requestData):
    # get the value after the "Host:" string
    hostStart = requestData.find(b'Host: ') + len(b'Host: ')
    hostEnd = requestData.find(b'\r\n', hostStart)
    hostString = requestData[hostStart:hostEnd].decode()

    # get the port
    portStart = hostString.find(':')
    webserverStart = hostString.find('/')

    if webserverStart == -1:
        webserverStart = len(hostString)

    if portStart == -1 or webserverStart < portStart:
        # default port
        port = 80
        host = hostString[0:webserverStart]
    else:
        # extract the specific port from the host string
        port = int((hostString[portStart + 1:])[0:webserverStart - portStart - 1])
        host = hostString[:portStart]

    return host, port

def handle_proxy_request(clientSocket):
    try:
        # receive client request
        requestData = clientSocket.recv(1024)

        if not requestData:
            clientSocket.close()
            return

        clientSocket.setBlocking(False)

        print("Request Data:")
        print(requestData.decode())

        # parse the request
        host, port = get_host_port(requestData)
        print(f"Host: {host}, Port: {port}")

        headers = requestData.decode().split('\r\n')
        firstHeader = headers[0].split(' ')
        method, url, version = firstHeader
        print(f"Method: {method}, URL: {url}, Version: {version}")

        

    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        clientSocket.close()


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

if __name__ == "__main__":
    start_tcp_proxy()