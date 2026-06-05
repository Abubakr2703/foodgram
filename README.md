# 🍽 Foodgram — продуктовый помощник и социальная сеть для гурманов

## Описание проекта
Foodgram — это современный продуктовый помощник, где пользователи могут публиковать рецепты, делиться кулинарным опытом, создавать персональные коллекции рецептов и формировать списки покупок.

## Автор

**Абубакр Алирзаев**  
- [GitHub](https://github.com/abubakr2703)  
- Email: `abubakr.alirzaev@yandex.ru`

## Технологии
- Python 3.11
- Django 5.1
- Django REST Framework
- Djoser (аутентификация по токенам)
- PostgreSQL
- Docker / Docker Compose
- GitHub Actions (CI/CD)
- Nginx

## Установка и запуск локально

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/abubakr2703/foodgram.git
cd foodgram
```
### Создайте файл .env в корне проекта и наполните его данными
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=ваш_пароль
DB_HOST=db
DB_PORT=5432

### Запустите контейнеры
```bash
cd infra
docker compose up -d
```
### Выполните миграции и соберите статику
```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
```

### Создайте суперпользователя (по желанию)
```bash
docker compose exec backend python manage.py createsuperuser
```
    После этого приложение будет доступно по адресу: http://localhost

### API
Документация API
После запуска проекта спецификация API доступна по адресу:
http://localhost/api/docs/

## Деплой на сервер
Проект настроен на автоматический деплой при пуше в ветку main через GitHub Actions.
После успешного выполнения workflow приложение доступно по адресу:

- IP: 81.26.179.232

## Админка Django
URL: http://81.26.179.232/admin/

 - Логин: abubakralirzaev69@gmail.com

- Пароль: 270376Abu

> В админке используется поле Email вместо имени пользователя (кастомная модель).


