import socket
import traceback
from Functions import func

MY_HOST = 'localhost'
MY_PORT = 9876
MAX_CLIENT_REQ = 30000
EXPECTED_PATH = '/api'
ALL_OPS = ["get", "post", "put", "delete"]

RESP_FORMAT = "HTTP/1.1 {0}\nContent-Type: text/html \n\n{1}"
RESP_FORMAT_ERROR = "HTTP/1.1 {0}\n"
ERROR_405 = "405 Method not allowed"
ERROR_404 = "404 Not Found"
ERROR_500 = "500 Internal server error"
ERROR_400 = "400 Bad Request"

def process_request(request):
        proc_req = {}
        proc_req["Request-type"] = {}
        proc_req["Par-path"] = {}
        proc_req["Simple-path"] = {}
        proc_req["Version"] = {}
        proc_req["Other_headers"] = {}
        proc_req["Params"] = {}
        proc_req["Body_Info"] = {}
        proc_req["Body"] = {}
        proc_req["Body_Info"]["Got_body"] = False
        """Process a request like: Get / HTTP/1.1"""
        first_line_in_req = request.strip().split("\n")[0]
        req_type = first_line_in_req.split()[0]
        path = first_line_in_req.split()[1].strip()
        """ Determine request type """
        proc_req["Request-type"] = req_type.strip().lower()
        """ Validation of request types """
        if proc_req["Request-type"] not in ["get", "post", "put", "delete"]:
            return  RESP_FORMAT.format(ERROR_404, "Method should be one of the following: get, post, put or delete.")
        """ Determine path of the request """
        proc_req["Par-path"] = path
        """ Determine simple path, without parameters """
        proc_req["Simple-path"] = path.split("?")[0].strip()
        """ In case my request is GET, determine parameters in the query URL"""
        params = proc_req["Par-path"].split("?")
        """ If I do have params, besides the path """
        if (len(params) > 1):
            params_list = params[1].split("&")
            for param_pair in params_list:
                key = param_pair.split("=")[0]
                val = param_pair.split("=")[1]
                proc_req["Params"][key] = val
        proc_req["Version"] = first_line_in_req.split()[2]
        #print("==========================================")
        for header_el in request.strip().split("\n")[1:]:
            header_el = header_el.strip()
            if len(header_el):
                print(header_el)
                if ":" in header_el:
                    key = header_el.split(":")[0]
                    value = header_el.split(":")[1]
                    proc_req["Other_headers"][key] = value
                else:
                    """ If I get the body in format x-www-form-urlencoded """
                    proc_req["Body_Info"]["Got_body"] = True
                    list = header_el.split("&")
                    for el in list:
                        key = el.split("=")[0]
                        value = el.split("=")[1]
                        proc_req["Body"][key] = value.strip()

        """ Validation of not any body in get request """
        if proc_req["Request-type"] == "get" and proc_req["Body_Info"]["Got_body"] == True:
            return RESP_FORMAT_ERROR.format(ERROR_404)

        print(proc_req["Simple-path"])
        print(EXPECTED_PATH)
        if proc_req["Simple-path"] == EXPECTED_PATH:
            if proc_req["Request-type"] in ALL_OPS:
                method = getattr(func, proc_req["Request-type"], None)
                if method is not None:
                    return method(proc_req)
                else:
                    return RESP_FORMAT.format(ERROR_405, "Method not implemented.")

        return RESP_FORMAT_ERROR.format(ERROR_500)

def start_server():
    """Start-up the server."""
    """Create a new socket using the given address family and socket type."""
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    """ Bind the socket to address """
    listen_socket.bind((MY_HOST, MY_PORT))
    """ Listen for connections made to the socket. Max bound: 1 """
    listen_socket.listen(1)

    print("Server alive on host{0} and port {1}".format(MY_HOST, MY_PORT))
    return listen_socket

def serve_client_requests(server):
    while True:
        """ Accept a connection -> new socket objects, address bound to the socket """
        conn, address = server.accept()
        request = str(conn.recv(MAX_CLIENT_REQ))
        print(request)
        #request = request.split("b'", 1)[1]
        try:
            http_response = process_request(request)
        except Exception as e:
            return RESP_FORMAT.format(ERROR_405, "Error:{0}".format(str(e)))
            traceback.print_exc()
        """ Returns the entire buffer passed or throws an exception """
        print(http_response)
        conn.sendall(http_response)
        conn.close()

def main():
    server = start_server()
    serve_client_requests(server)

if __name__ == "__main__":
    main()