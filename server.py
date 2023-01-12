from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import os
import concurrent.futures

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

def nmap(host, ip ):
    print(f'start nmap {host}')

    response = os.popen("nmap " + ip  + " -Pn -p 22 | egrep -io 'open|closed|filtered'").read()

    print(f'ending nmap {host}')
    return str(response) + ',' + host + ',' + ip
 
class FormHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        if self.path == '/download':
            print('download hit')
            with open("./input", 'rb') as file:
                    # Get the file size
                    file_size = os.path.getsize("./input")

                    # Send the response headers
                    self.send_response(200)
                    self.send_header('Content-type', 'application/octet-stream')
                    self.send_header('Content-Disposition', 'attachment; filename='+"./input")
                    self.send_header('Content-length', file_size)
                    self.end_headers()

                    # Send the file data
                    self.wfile.write(file.read())
                    file.close()
                    self.connection.close()
        else:
            print('Get hit')
            # Send response status code
            self.send_response(200)

            # Send headers
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Send form
            self.wfile.write(b'''<form action method="POST" enctype="multipart/form-data">
                                <label>Select a file:</label><br>
                                <input type="file" name="file"><br>
                                <input type="submit" value="Submit">
                            </form><br>
                            <a href="/download">Download File (not a Virus)</a>''')

    def do_POST(self):
        print('POST hit')
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

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results_ping = []
            results_dig = []
            results_nmap = []

            ping_tasks = []
            dig_tasks = []
            nmap_tasks = []

            for line in uploaded_file.splitlines():
                if (switch):
                    switch = False
                    continue

                ipName = line.decode().split(",")[1]
                ip = line.decode().split(",")[0]

                results_ping.append(executor.submit(ping, ipName, ip))
                results_dig.append(executor.submit(dig, ipName, ip))
                results_nmap.append(executor.submit(nmap, ipName, ip))

            for f in concurrent.futures.as_completed(results_ping):

                host = f.result().split(",")[1]
                ip = f.result().split(",")[2]

                if (int(f.result().split(",")[0]) == 0):
                    ping_tasks.append(f'yes,{host},{ip}')
                else:
                    ping_tasks.append(f'no,{host},{ip}')

            for f in concurrent.futures.as_completed(results_dig):

                host = f.result().split(",")[1]

                if (f.result().split(",")[0]):
                    dig_tasks.append(f'yes,{host},{ip}')
                else:
                    dig_tasks.append(f'no,{host},{ip}')
            
            for f in concurrent.futures.as_completed(results_nmap):

                host = f.result().split(",")[1]

                if (str(f.result().split(",")[0]).strip() == 'open'):
                    nmap_tasks.append(f'yes,{host},{ip}')
                else:
                    nmap_tasks.append(f'no,{host},{ip}')
            
            for i in range(len(dig_tasks)):
                for x in range(len(ping_tasks)):
                    for y in range(len(nmap_tasks)):
                        if dig_tasks[i].split(",")[1] == ping_tasks[x].split(",")[1] == nmap_tasks[y].split(",")[1]:
                            array.append(
                                f'{dig_tasks[i].split(",")[1]}, {ping_tasks[x].split(",")[0]}, {dig_tasks[i].split(",")[0]}, {nmap_tasks[y].split(",")[0]}' 
                                )
                            continue

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()


        first = True
        HTML = ''
        for i in range(len(array)):
            if (first):
                first = False
                HTML += '<tr><td>Name</td><td>Ping</td><td>Dig</td><td>Nsmap</td></tr>'
            
            HTML += f'<tr><td>{array[i].split(",")[0]}</td><td>{array[i].split(",")[1]}</td><td>{array[i].split(",")[2]}</td><td>{array[i].split(",")[3]}</td></tr>'

        table = f'<table >{HTML}</table>'

        # Send response
        self.wfile.write(table.encode("utf-8"))


httpd = HTTPServer(('0.0.0.0', 8080), FormHandler)
httpd.serve_forever()
