import socket

HOST = "127.0.0.1"
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST,PORT))
    s.listen(1)
    try:
        while True:
            conn, adr = s.accept()
            with conn:
                print("Connected by", adr)
                data = conn.recv(1024)
                if not data: break
                print(data.decode("utf-8"))
                with open("index.html", "r") as file:
                    file_data = file.read()
                    send_data = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
                    send_data += file_data
                    conn.sendall(send_data.encode("utf-8"))
    except Exception as e:
        print(e)
        s.close()

