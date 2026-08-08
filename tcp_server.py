from socket import *
from datetime import datetime, timezone
import os

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

        # Parse the request line 
        lines = request.split("\r\n")
        method, path, version = lines[0].split() # lines[0] is the request line

        # Map the URL path to a local file
        if path == "/":
            filename = "test.html"
        else:
            filename = path.lstrip("/")

        # sentence = connectionSocket.recv(1024).decode()
        # capitalizedSentence = sentence.upper()

        # 505 - HTTP Version Not Supported; when user request is not HTTP1.1
        if version != "HTTP/1.1":
            response = "HTTP/1.1 505 HTTP Version Not Supported\r\n\r\n"
            connectionSocket.send(response.encode())
            connectionSocket.close()
            continue

        try:
            with open(filename, "rb") as f:
                body = f.read()
        except FileNotFoundError:
            # 404 - Not Found; when user request for something that does not exist
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            connectionSocket.send(response.encode())
            connectionSocket.close()
            continue
        except PermissionError:
            # 403 - Forbidden; when user request does not have permission to access
            response = "HTTP/1.1 403 Forbidden\r\n\r\n"
            connectionSocket.send(response.encode())
            connectionSocket.close()
            continue

        # 304 - Not Modified; when user request has "If-Modified-Since"

        # Find If-Modified-Since header
        ims_value = None
        for line in lines[1:]:
            if line.lower().startswith("if-modified-since:"):
                ims_value = line.split(":", 1)[1].strip()
                break

        mtime = datetime.fromtimestamp(os.path.getmtime(filename), timezone.utc).replace(microsecond=0) # File's actual modified time
        if ims_value:
            ims = datetime.strptime(ims_value, "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=timezone.utc)
            # The file was last modified at or before the client's date - File hasn't changed since the client's copy
            if mtime <= ims:
                response = "HTTP/1.1 304 Not Modified\r\n\r\n"
                connectionSocket.send(response.encode())
                connectionSocket.close()
                continue

        # 200 - OK; everything checks out correctly
        last_modified = mtime.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = "HTTP/1.1 200 OK\r\n"
        response += f"Last-Modified: {last_modified}\r\n"
        response += "\r\n"
        connectionSocket.send(response.encode() + body)
        # connectionSocket.send(capitalizedSentence.encode())

        connectionSocket.close()

if __name__ == "__main__":
    start_tcp_server()