# 1. Установка, настройка и наполнение Базы данных
## 1.1. Установка СУБД PostgreSQL
### Вариант 1. Установка и запуск в ОС Windows
1. Скачать дистрибутив:<br/>
https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
2. Установить дистрибутив отметив следующие пункты:<br/>
   - PostgreSQL Server<br/>
   - PgAdmin<br/>
   - Command Line Tools
3. В процессе установки задать и запомнить пароль для стандартного администратора ***postgres***
4. Перейти в каталог:<br/>
```sh
cd C:\Program Files\PostgreSQL\#Номер версии#\bin
```
5. Открыть консоль ***PostgreSQL***:
```sh
psql -U postgres
```

### Вариант 2. Установка и запуск в ОС Linux
1. Установить пакет ***libpq-dev***:
```sh
sudo apt install libpq-dev
```
2. Установить пакет ***Postgres*** вместе с пакетом ***-contrib***:
```sh
sudo apt install postgresql postgresql-contrib
``` 
5. Открыть консоль ***PostgreSQL***:
```sh
sudo -u postgres psql postgres
```
6. Задать пароль для стандартного администратора ***postgres***:
```sh
\password postgres
```

### Вариант 3. Установка и запуск в Mac OS
1. Установить пакет ***PostgreSQL***:
```sh
brew install postgres
```
2. Создать пользователя ***postgres***:
```sh
/usr/local/opt/postgres/bin/createuser -s postgres
```
3. Открыть консоль ***PostgreSQL***:
```sh
psql postgres
```
4. Задать пароль для стандартного администратора ***postgres***:
```sh
\password postgres
```

## 1.2. Настройка СУБД PostgreSQL
1. Создать пользователя ***scrum*** с паролем ***django***:
```sh
create user scrum with password 'django';
alter role scrum set client_encoding to 'utf8';
alter role scrum set default_transaction_isolation to 'read committed';
alter role scrum set timezone to 'UTC';
```
2. Создать базу данных ***scrum_db*** с владельцем ***scrum***:
```sh
create database scrum_db owner scrum;
```
3. Обновить зависимости согласно файлу requirements.txt
## 1.3. Миграции и  наполнение данными

Для выполнения процедуры создания базы данных и наполнения тестовыми данными необходимо выполнить следующую команду:

```sh
python manage.py fill_db        # Для Windows
python3 manage.py fill_db       # Для Mac OS / Linux
```

# Готовый проект
Ссылка на актуальную версию ветки main данного проекта: http://inengb.ru/
