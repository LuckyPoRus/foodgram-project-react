<h1 align="center">Foodgram</h1>

## Описание проекта
Сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд и перед походом в магазин скачивать его в формате txt.

## Используемые технологии:
- Django - 4.1.7
- Django Rest Framework - 3.14.0
- Python 3.10.10
- PostgreSQL
- Docker
- Gunicorn
- Nginx
- Yandex.Cloud

## Как запустить проект:
### Локально:
1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:LuckyPoRus/foodgram-project-react.git
```
2. Переход в директорию и активация виртуального окружения:
```
cd foodgram-project-react
```
3. Создание и активация виртуального окружения:
```
python -m venv venv
source venv/scripts/activate
```
4. Обновление pip и установка зависимостей:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
5. Создание образа фронтенда и бэкенда:
```
cd ./frontend/
docker build -t <your_username>/<foodgram_frontend> .
cd ./backend/
docker build -t <your_username>/<foodgram_backend> .
```
6. Запуск контейнеров:
```
cd ./infra/
docker-compose up -d
```
7. После успешного запуска контейнеров необходимо выполнить миграции, <br/>
создать суперпользователя и собрать статику:
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
```
8. Проверить работу сервиса:
[http://127.0.0.1](http://127.0.0.1)

### На сервере:
1. Выполнить шаги с 1 по 5 из предыдущего пункта.
2. Отправить образы на свой Dockerhub:
```
docker login
docker push <your_username>/<foodgram_frontend>
docker push <your_username>/<foodgram_backend>
```
3. Подключение к серверу :
```
ssh <username>@<server_public_ip>
```
4. Отредактировать файл nginx.conf (в строке server_name указать свой адрес сервера),<br/>
скопировать подготовленные файлы docker-compose.yml и nginx.conf:
```
scp docker-compose.yaml <username>@<server_public_ip>:/home/<username>/
sudo mkdir nginx
scp nginx.conf <username>@<server_public_ip>:/home/<username>/nginx/
```
5. Установть docker и docker-compose:
```
sudo apt install docker.io
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
6. Выполнить ```git push``` на локальном компьютере, запустится процесс workflow.
7. После успешного запуска контейнеров на сервере необходимо выполнить миграции, <br/>
создать суперпользователя и собрать статику:
```
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
8. Наполнить базу тестовыми данными:
```
sudo docker-compose exec backend python manage.py loaddata foodgram_new.json
```

**Автор backend составляющей:**<br/>
**Павел** - https://github.com/LuckyPoRus
**Ссылка на проект:** <http://158.160.57.56/>
![example workflow](https://github.com/LuckyPoRus/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)<br>
