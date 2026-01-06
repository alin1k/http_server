import socket
import os
from utils import headers_str_to_dict, get_mime_type, http_response

class HttpServer:
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path_map = {}

    def __init__(self):
        pass

    @staticmethod
    def send(body, **options):
        headers = options.get('headers', {})
        headers.setdefault("Content-Type", "text/plain")
        headers.setdefault("Content-Length", len(body))

        return http_response(headers, body, options.setdefault("status", 200))

    def send_file(self, req_path, **options):
        file_path = os.path.join(self.ROOT_DIR, "static", req_path.lstrip("/"))
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()
                mime_type = get_mime_type(file.name)
                headers = options.get('headers', {})
                headers.setdefault("Content-Type", mime_type)

                response = self.send(file_data, headers=headers)
        except FileNotFoundError:
            response = self.send("Not found", status=404)

        return response

    def listen(self, port, host="127.0.0.1"):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen(1)

            print(f"Server started on: {host}:{port}\n\n\n")

            while True:
                conn, adr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        continue

                    data = data.decode("utf-8")
                    print(data)

                    req_start_line = data.split("\r\n")[0].split(" ")

                    req_method = req_start_line[0]
                    req_path = req_start_line[1]
                    req_headers = headers_str_to_dict(data.split("\r\n", 1)[1].split("\r\n\r\n")[0])

                    try:
                        if self.path_map.get(req_path, False):
                            response = self.path_map[req_path][req_method]()
                        else:
                            response = self.send_file(req_path, **req_headers)
                    except Exception as e:
                        print(f"\n\nAn error occurred [{req_path}]:", e, "\n\n")
                        response = self.send("Internal server error", status=500)

                    conn.sendall(response)

    def route(self, path, methods=["GET"]):
        def route_decorator(route_func):
            def route_wrapper(*args, **kwargs):
                return route_func(*args, **kwargs)

            self.path_map.update({
                path: {method: route_wrapper for method in methods}
            })

            return route_wrapper
        return route_decorator