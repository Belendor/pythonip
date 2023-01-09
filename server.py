from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import os
import asyncio


async def ping(host):
    # Run the ping command
    process = await asyncio.create_subprocess_exec(
        "ping", "-c", "1", host, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    # Wait for the ping command to complete
    stdout, stderr = await process.communicate()
    # Return the output of the ping command
    return stdout


class FormHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
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
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        # Save the file to a variable
        file_item = form['file']
        uploaded_file = file_item.file.read()

        switch = True
        array = []

        for line in uploaded_file.splitlines():
            if (switch):
                first_line = line.decode()
                switch = False
                array.append('Name, Ping')
                continue
            
            ipName = line.decode().split(",")[1]
            response = asyncio.run(ping(ipName))

            # response = await asyncio.os.system("ping -c 1 " + line.decode().split(",")[1])
            if (response):
                array.append(f'{ipName}, Yes')
            else:
                array.append(f'{ipName}, No')
            # print(response)

            # Process the line
            # print(line.decode())

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        kas = ", <br>".join(array)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print(kas)
        # Send response
        self.wfile.write(kas.encode("utf-8"))


httpd = HTTPServer(('0.0.0.0', 8080), FormHandler)
httpd.serve_forever()
