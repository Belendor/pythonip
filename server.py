from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import os
import asyncio
import concurrent.futures
import time

def ping(host, ip):
    print(f'start ping {host}')

    response = os.system("ping -c 1 " + host + " 1>/dev/null 2>/dev/null")

    print(f'ending ping {host}')
    return str(response) + ',' + host + ',' + ip

def dig(host, ip ):
    print(f'start dig {host}')

    response = os.popen("dig " + host + " +short").read()

    print(f'ending dig {host}')
    return str(response) + ',' + host + ',' + ip
 
class FormHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Send form
        self.wfile.write(b'''<form method="POST" enctype="multipart/form-data">
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
        ping_tasks = []
        dig_tasks = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results_ping = []
            results_dig = []

            for line in uploaded_file.splitlines():
                if (switch):
                    switch = False
                    array.append('Name, Ping, Dig')
                    continue

                ipName = line.decode().split(",")[1]
                ip = line.decode().split(",")[0]

                results_ping.append(executor.submit(ping, ipName, ip))
                results_dig.append(executor.submit(dig, ipName, ip))


            for f in concurrent.futures.as_completed(results_ping):

                host = f.result().split(",")[1]
                ip = f.result().split(",")[2]

                if (int(f.result().split(",")[0]) == 0):
                    ping_tasks.append(f'yes,{host},{ip}')
                else:
                    ping_tasks.append(f'no,{host},{ip}')

            for f in concurrent.futures.as_completed(results_dig):

                host = f.result().split(",")[1]

                # print('>>>>>>>>>>>>>>>>>>>')
                # print(f.result())

                if (f.result().split(",")[0]):
                    dig_tasks.append(f'yes,{host},{ip}')
                else:
                    dig_tasks.append(f'no,{host},{ip}')
            
            for i in range(len(dig_tasks)):
                for x in range(len(ping_tasks)):
                    if dig_tasks[i].split(",")[1] == ping_tasks[x].split(",")[1]:
                        array.append(
                            f'{dig_tasks[i].split(",")[1]}, {ping_tasks[x].split(",")[0]}, {dig_tasks[i].split(",")[0]}' 
                            )

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Send response
        self.wfile.write(", <br>".join(array).encode("utf-8"))


httpd = HTTPServer(('0.0.0.0', 8080), FormHandler)
httpd.serve_forever()
