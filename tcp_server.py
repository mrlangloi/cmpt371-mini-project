from socket import *

# Logic to generate each status code + HTTP request message to test (using `curl -v` in a terminal).
# -v flag is to set "verbose mode", which shows details of the req/res exchange.

# 200 - OK
#   logic:  The HTTP request passes all checks for status codes (304, 403, 404, and 505).
#           Return 200 response header with the file as the body.
#   test:   curl -v http://localhost:12000/test.html

# 304 - Not Modified
#   logic:  If "If-Modified-Since" header is in the request, compare it with the file's timestamp.
#           Return 304 response header without a body if the file timestamp is older than request timestamp.
#   test:   curl -v --header "If-Modified-Since: Mon, 21 Jul 2026 00:00:00 GMT" http://localhost:12000/test.html

# 403 - Forbidden
#   logic:  Check if the file exists, and if it does check if the request is permitted to access it.
#           Return 403 if the request is not authorized to access the file.
#   test:   curl -v http://localhost:12000/data

# 404 - Not Found
#   logic:  Check if the file exists.
#           Return 404 if the file does not exist.
#   test:   curl -v http://localhost:12000/notfound.html

# 505 - HTTP Version Not Supported
#   logic:  Check the HTTP version number of the request.
#           Return 505 if the request's version is not supported
#   test:   curl -v --http1 http://localhost:12000/test.html

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