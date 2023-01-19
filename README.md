# Nginx REverse Proxy

`/etc/nginx/sites-available/defaul`

`server {
    listen 80;
    listen [::]:80;
    server_name _;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

#    listen 443 ssl;
#    listen [::]:443 ssl;
#    ssl_certificate /etc/ssl/certs/your_ssl_certificate.crt;
#    ssl_certificate_key /etc/ssl/private/your_ssl_key.key;
#    ssl_protocols TLSv1.2;
#    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
#    ssl_prefer_server_ciphers on;
}`
