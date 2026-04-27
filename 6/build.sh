#!/bin/bash

sudo docker rm -f pg-db my-parser-app 2>/dev/null

docker network create parser-net 2>/dev/null || true

sudo tee /etc/nginx/sites-available/parser-proxy > /dev/null << 'EOF'
server {
    listen 80;
    server_name localhost _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/parser-proxy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t
sudo service nginx restart

docker run --name pg-db \
  --network parser-net \
  --env-file .env \
  -d postgres:15

until docker exec pg-db pg_isready -U postgres; do
  sleep 2
done

docker build -t github-parser-app .

docker run --name my-parser-app \
  --network parser-net \
  --env-file .env \
  -p 8080:8001 \
  -d github-parser-app

echo "Containers started"
