## Геренация ssh-ключа
```
ssh-keygen -t rsa -b 4096
```
## Копирование публичного ключа на удалённый сервер
```
ssh-copy-id -p 10023 t.ilinyh@84.237.51.129
```
## Пуш файла на удалённый репозиторий
### Клонирование репозитория на локальную машину
```
git clone git@github.com:TatianaIl05/computer_networks.git
cd computer_networks
```
### Настройка глобального имени пользователя и почты
```
git config --global user.name TatianaIl05
git config --global user.email t.ilinykh1@g.nsu.ru
```
### Добавление файла в область подготовки, сохранение изменений в лкальном репозитории и пуш в удалённый репозиторий на гитхаб 
```
echo "This is a push into remote repository without password" >> 2/some_test.txt
git add 2/some_test.txt
git commit -m "added file remotely"
git push
```
