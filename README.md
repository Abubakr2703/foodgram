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

### Установка
```bash
git clone https://github.com/abubakr2703/foodgram
cd foodgram
```

### Переменные окружения

Создайте файл `.env` в корне проекта

```bash
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=ваш_пароль
DB_HOST=db
DB_PORT=5432
```

### Запуск через Docker
```bash
cd infra
docker compose up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py createsuperuser
```
Приложение будет доступно по адресу: http://localhost

## Деплой на сервер
проект будет доступе по IP - 81.26.179.232
админка будет доступна по http://81.26.179.232/admin/
логин и пароль:
login: abubakralirzaev69@gmail.com
password: 270376Abu