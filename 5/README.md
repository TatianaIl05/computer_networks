```
docker network create quotes-network
docker build --no-cache -t quotes-app .
docker run -d \
  --name postgres-db \
  --network quotes-network \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=quotes_db \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:15
docker run -d \
  --name quotes-app \
  --network quotes-network \
  -e DB_HOST=postgres-db \
  -e DB_NAME=quotes_db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e QUOTES_USERNAME=admin \
  -e QUOTES_PASSWORD=admin \
  -e HEADLESS=true \
  -p 8001:8001 \
  quotes-app
```
```
curl "http://localhost:8001/parse?url=https://quotes.toscrape.com"
```
```
curl "http://localhost:8001/get_data"
```
```
curl -X DELETE "http://localhost:8001/clean_db?confirm=true"
```
Для удаления:
```
docker stop quotes-app postgres-db 2>/dev/null
docker rm quotes-app postgres-db 2>/dev/null
docker network rm quotes-network 2>/dev/null
```
