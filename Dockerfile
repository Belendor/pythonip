FROM python
EXPOSE 8080
WORKDIR /app
COPY . /app
CMD [ "python" , "server.py"]