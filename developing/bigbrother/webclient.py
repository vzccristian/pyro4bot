import webview
import socket
import threading


def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except Exception:
        return False


class webView(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.launchWebView()

    def launchWebView(self):
        if isOpen(self.ip, self.port):

            webview.create_window("BigBrother monitor", url="http://" +
                                  self.ip + ":" + str(self.port),
                                  confirm_quit=True)


if __name__ == "__main__":
    ip = "192.168.10.1"
    port = 80
    wv = webView(ip, port)
