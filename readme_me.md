# readme_me (Developer Deploy Guide)

Этот файл для тебя: полный сценарий подготовки, деплоя, обновлений и диагностики.

## 1. Быстрая схема
1. Локально проверить проект.
2. Запушить в GitHub.
3. На сервере: `git clone` -> `.env` -> `docker compose up --build -d`.
4. Настроить Nginx + SSL.
5. Отдать проверяющему ссылку + админ доступ.

## 2. Локальная подготовка

```powershell
cd C:\Users\vovan\PycharmProjects\TestovoePythonDjangoStripe
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test payments.tests -v 2
```

## 3. `.env` для локали

```env
DJANGO_SECRET_KEY=<local-random-secret>
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
DOMAIN_URL=http://127.0.0.1:8000

STRIPE_DEFAULT_CURRENCY=usd
STRIPE_SECRET_KEY_USD=sk_test_xxx
STRIPE_PUBLISHABLE_KEY_USD=pk_test_xxx
STRIPE_SECRET_KEY_RUB=sk_test_xxx
STRIPE_PUBLISHABLE_KEY_RUB=pk_test_xxx
```

Сгенерировать Django secret key:

```powershell
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 4. GitHub push

```bash
git add .
git commit -m "Prepare project for deployment"
git push
```

## 5. Серверный деплой через Docker (Ubuntu)

### 5.1 Установить Docker

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg git
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
sudo apt install -y docker-compose-plugin
```

### 5.2 Клонировать проект

```bash
git clone https://github.com/<username>/<repo>.git
cd <repo>
```

### 5.3 Создать production `.env`

```bash
cp .env.example .env
nano .env
```

Пример:

```env
DJANGO_SECRET_KEY=<prod-random-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
DOMAIN_URL=https://your-domain.com

STRIPE_DEFAULT_CURRENCY=usd
STRIPE_SECRET_KEY_USD=sk_test_or_live_xxx
STRIPE_PUBLISHABLE_KEY_USD=pk_test_or_live_xxx
STRIPE_SECRET_KEY_RUB=sk_test_or_live_xxx
STRIPE_PUBLISHABLE_KEY_RUB=pk_test_or_live_xxx
```

### 5.4 Поднять сервис

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f --tail=200
```

## 6. Домен и SSL

### 6.1 Nginx reverse proxy

`/etc/nginx/sites-available/testovoe`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/testovoe /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6.2 SSL

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 7. Обновления после новых коммитов

```bash
cd <repo>
git pull
docker compose up --build -d
docker compose logs -f --tail=200
```

## 8. Откат

```bash
cd <repo>
git log --oneline
git checkout <stable_commit_hash>
docker compose up --build -d
```

## 9. Что отправлять проверяющему
1. URL приложения
2. URL админки
3. Логин/пароль админки
4. GitHub репозиторий
5. Указать, что есть Docker + env + бонусные endpoints

## 10. Частые ошибки
- `Invalid API Key provided` -> неверный или не тот режим ключа.
- `Stripe secret key is missing for currency` -> не заполнена переменная для валюты.
- CSRF/Host ошибки -> неверные `DJANGO_ALLOWED_HOSTS`/`DJANGO_CSRF_TRUSTED_ORIGINS`.
- 404 `/item/1/` -> нет товара с id=1.
