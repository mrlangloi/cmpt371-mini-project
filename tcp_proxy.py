from socket import *
import threading

serverPort = 12001
PROXY_LISTEN = 10
BYTES_RECEIVED = 1024

cache = {}

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

def get_path(url: String):
    if url.startswith("http://") or url.startswith("https://"):
        # split https://localhost:8080/index.html into ["https", "localhost:8080/index.html"]
        urlSplit = url.split("://")
        if len(urlSplit) == 2:
            # find the position of the slash after the port
            pathStart = urlSplit[1].find("/")

            if pathStart == -1:
                # no path, return "/"
                return "/"
            else:
                # return the path
                return urlSplit[1][pathStart:]

    return url

def get_last_modified(responseData):
    headers = responseData.decode().split('\r\n')
    for header in headers:
        if header.lower().startswith('last-modified:'):
            return header.split(':')[1]
    return None

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
        path = get_path(url)
        print(f"Method: {method}, URL: {url}, Path: {path}, Version: {version}")

        # cache lookup
        data = None
        lastModified = None
        if url in cache:
            data, lastModified = cache[url]

        # create a conditional GET to origin server to check if file is up-to-date
        conditionalGet = f"{method} {path} {version}\r\n"
        conditionalGet += f"Host: {host}\r\n"
        if lastModified:
            conditionalGet += f"If-Modified-Since: {lastModified}\r\n"

        # create socket to connect to origin server
        originSocket = socket(AF_INET, SOCK_STREAM)
        originSocket.connect((host, port))

        # forward the conditional GET request to the origin server
        originSocket.sendall(conditionalGet.encode())

        # build the server's response
        response = b""
        while True:
            responseData = originSocket.recv(BYTES_RECEIVED)
            if not responseData:
                break
            response += responseData

        # check the origin server response
        if "304 Not Modified" in response and (url in cache):
            # cache has up-to-date version, send that instead
            print("304 Not Modified, sending cached version instead")
            clientSocket.send(data)
        elif "200 OK" in response:
            # cache has stale version, update cache
            print("200 OK, updating cache and before responding")
            newLastModified = get_last_modified(response)
            cache[url] = (response, newLastModified)
            clientSocket.send(response)
        else:
            # origin server sent back either 403, 404, or 505
            clientSocket.send(response)

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