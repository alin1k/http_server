from server import HttpServer

server = HttpServer()

@server.route(path="/", methods=["GET"])
def index():
    return server.send_file("index.html")

@server.route(path="/test", methods=["GET"])
def test():
    return server.send("Merge!!! URAAa")

server.listen(8080)