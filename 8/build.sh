#!/bin/bash

sudo docker rm -f pg-db my-parser-app 2>/dev/null

docker network create parser-net 2>/dev/null || true

sudo mkdir -p /etc/nginx/conf.d/geo_lists
curl -s https://www.ipdeny.com/ipblocks/data/aggregated/ru-aggregated.zone | 
    awk '{print "    " $0 " 1;"}' | 
    sudo tee /etc/nginx/conf.d/geo_lists/ru_ips.conf > /dev/null

sudo tee /etc/nginx/conf.d/parser-proxy.conf > /dev/null << 'EOF'
geo $is_ru {
    default 0;
    include /etc/nginx/conf.d/geo_lists/ru_ips.conf;
    # 127.0.0.1 1;    
}

server {
    listen 80;
    server_name localhost _;

    location = /blocked {
        # internal;
        add_header Content-Type "text/html; charset=utf-8";
        return 200 '<h1>ВАМ СЮДА НЕЛЬЗЯ</h1>';
    }

    location /debug {
        return 200 "is_ru = $is_ru\n";
    }

    location / {
         if ($is_ru) {
            return 307 /blocked;
         }
        
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
