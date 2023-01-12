FROM python
EXPOSE 8080
WORKDIR /app
COPY . /app
RUN apt-get update
RUN apt-get install nmap -y
RUN apt-get install dnsutils -y
RUN apt-get install iputils-ping -y
CMD [ "python" , "server.py"]