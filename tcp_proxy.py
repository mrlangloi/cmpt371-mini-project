from socket import *
import threading

serverPort = 12001
PROXY_LISTEN = 10
BYTES_RECEIVED = 1024

# e.g., b"GET /api/v1 HTTP/1.1\r\nHost: localhost:8080\r\nAccept: */*\r\n\r\n"
# returns ('localhost', 8080)
def get_host_port(requestData):
    requestDataLower = requestData.lower()

    # get the value after the "host:" string
    hostStart = requestDataLower.find(b'host: ') + len(b'host: ')
    hostEnd = requestData.find(b'\r\n', hostStart)
    hostString = requestData[hostStart:hostEnd].decode()

    # split and return the host and port
    if ':' in hostString:
        # localhost:8080 into ('localhost', 8080)
        host, portString = hostString.split(':', 1)
        port = int(portString)
    else:
        # localhost into ('localhost', 80)
        host = hostString
        port = 80

    return host, port

def handle_proxy_request(clientSocket: socket):
    try:
        # receive client request
        requestData = clientSocket.recv(BYTES_RECEIVED)

        if not requestData:
            clientSocket.close()
            return

        print("Request Data:")
        print(requestData.decode())

        # parse the request
        host, port = get_host_port(requestData)
        print(f"Host: {host}, Port: {port}")

        headers = requestData.decode().split('\r\n')
        firstHeader = headers[0].split(' ')
        method, url, version = firstHeader
        print(f"Method: {method}, URL: {url}, Version: {version}")

        # create socket to connect to origin server
        originSocket = socket(AF_INET, SOCK_STREAM)
        originSocket.connect((host, port))

        # forward the request to the origin server
        originSocket.sendall(requestData)

        while True:
            response = originSocket.recv(BYTES_RECEIVED)
            # print("Response Data:")
            # print(response.decode())

            if not response:
                break

            if len(response) > 0:
                clientSocket.sendall(response)
            else:
                break

        originSocket.close()

    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        clientSocket.close()


def start_tcp_proxy():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(PROXY_LISTEN)
    print("The proxy is ready to receive")

    while True:
        connectionSocket, addr = serverSocket.accept()
        print("Connection received from:", addr)

        # process the request
        clientHandler = threading.Thread(target=handle_proxy_request, args=(connectionSocket,))
        clientHandler.start()

if __name__ == "__main__":
    start_tcp_proxy()