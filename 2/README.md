```
ssh-keygen -t rsa -b 4096
```
```
ssh-copy-id -p port username@hostname
```
in my case:
```
ssh-copy-id -p 10023 t.ilinyh@host
```
```
git clone git@github.com:TatianaIl05/computer_networks.git
cd computer_networks
git config --global user.name TatianaIl05
git config --global user.email t.ilinykh1@g.nsu.ru
echo "This is a push into remote repository without password" >> 2/some_test.txt
git add 2/some_test.txt
git commit -m "added file remotely"
git push
```
