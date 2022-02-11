#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

from ast import parse
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
#import pdb

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):        
        return data[9:12]

    def get_headers(self,data):
        return None

    def get_body(self, data):
        bodyStartPos = data.find("\r\n\r\n")
        return data[bodyStartPos+4:]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer
        #return buffer.decode('utf-8')# doesn't work with google

    def parseUrl(self, url):
        parseResult = urllib.parse.urlparse(url)
        host = parseResult.netloc
        #port
        port  = parseResult.port
        if parseResult.port == None:
            if parseResult.scheme == "http":
                port = 80
            elif parseResult.scheme == "https":
                port = 443
            else:
                raise Exception("No scheme given in URL (http or https?)")  
        #path
        path = parseResult.path
        if path == "":
            path = "/"

        return host, port, path

    def getResp(self):
        respBuffer = self.recvall(self.socket)
        try:
            resp = respBuffer.decode("utf-8")
        except:#google.com?
            resp = respBuffer.decode("latin-1")

        self.close()

        code = self.get_code(resp)
        body = self.get_body(resp)
        return code, body

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.parseUrl(url)
        self.connect(host, port)

        msg = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nConnection: close\r\n\r\n"
        self.sendall(msg)

        code, body = self.getResp()

        return HTTPResponse(code, body)


    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.parseUrl(url)
        self.connect(host, port)

        if not args:
            args = ""
        else:
            args = urllib.parse.urlencode(args)

        msg =f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(args)}\r\nConnection: close\r\n\r\n{args}"
        self.sendall(msg)

        code, body = self.getResp()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
