## Настройка сервера (AlmaLinux):
### Подключение к серверу
```
ssh root@IP_вашего_сервера
```
### Установка Docker
```
dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable docker
systemctl start docker

# Проверяем
docker --version
```
### Установка Nginx
```
dnf install -y nginx
systemctl enable nginx
systemctl start nginx
```

### С ПК скопировать проект на сервер
```
# На ПК в папке с проектом
tar -czf project.tar.gz .
scp project.tar.gz root@IP_сервера:~/
```
```
# На сервере
tar -xzf project.tar.gz
ls -la  # проверить, что все файлы на месте
```
### Отключение дефолтного конфига
```
rm -f /etc/nginx/conf.d/default.conf
```
### Запуск контейнеров
```
chmod +x build.sh
./build.sh
```

### Просмотр результатов (блок российских IP):

http://178.20.47.174/get_data - просмотреть данные после парсинга
http://178.20.47.174/get_data - запустить парсинг

curl -X DELETE "http://178.20.47.174/clean_db?confirm=true"- удалить данные
