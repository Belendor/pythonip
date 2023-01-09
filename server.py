#!/usr/bin/env python

from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import os

class FormHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Send response status code
        self.send_response(200)
 
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()
 
        # Send form
        self.wfile.write(b'''<form action="http://127.0.0.1:8080" method="POST" enctype="multipart/form-data">
                            <label>Select a file:</label><br>
                            <input type="file" name="file"><br>
                            <input type="submit" value="Submit">
                        </form>''')
        
    def do_POST(self):
        # Parse the form data
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
 
        # Save the file to a variable
        file_item = form['file']
        uploaded_file = file_item.file.read()
        
        switch = True
        switch1 = True
        first_line = ''
        second_line = ''
        
        for line in uploaded_file.splitlines():
            if (switch):
                first_line = line.decode()
                switch = False
                continue
            
            if (switch1):
                second_line = line.decode().split(",")
                switch1 = False
                
                response = os.system("ping -c 1 " + second_line[1])
                
                continue
            
            # Process the line
            print(line.decode())
 
        # Send response status code
        self.send_response(200)
 
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()
 
        # Send response
        self.wfile.write(str(response).encode("utf-8"))

httpd = HTTPServer(('0.0.0.0', 8080), FormHandler)
httpd.serve_forever()