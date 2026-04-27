```
sudo sed -i 's/default 0;/default 1;/' /etc/nginx/sites-available/parser-proxy
sudo service nginx restart
curl http://localhost/parse?url=https://quotes.toscrape.com
```
307 редирект (все заблокированы)
```
curl -L http://localhost/parse?url=https://quotes.toscrape.com
```
<h1>ВАМ СЮДА НЕЛЬЗЯ</h1>
```
sudo sed -i 's/default 1;/default 0;/' /etc/nginx/sites-available/parser-proxy
sudo service nginx restart
```
{"status":"success","message":"Successfully parsed and saved 20 quotes","pages_parsed":2,"quotes_saved":20,"source_url":"https://quotes.toscrape.com"}
