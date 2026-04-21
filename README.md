# README For Reviewer (Quick Run + Usage)

Этот файл для быстрой проверки задания.
Приоритет проверки обычно такой:
1. Готовый удаленный стенд (ссылка, уже работает)
2. Локальный запуск через Python (без Docker)
3. Docker (как дополнительный способ)

## 1. Если уже есть развернутый сервер (предпочтительно)

Откройте ссылки:
- Приложение: `https://<your-domain>`
- Админка: `https://<your-domain>/admin/`
- Пример товара: `https://<your-domain>/item/1/`

Для входа в админку используйте переданные логин/пароль.

## 2. Локальный запуск без Docker (основной локальный способ)

### 2.1 Требования
- Python 3.12+
- Git

### 2.2 Шаги

```bash
git clone https://github.com/<username>/<repo>.git
cd <repo>
cp .env.example .env
```

Заполнить `.env` (минимум Stripe test keys).

#### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

#### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Сервис будет на `http://127.0.0.1:8000`.

## 3. Запуск через Docker (опционально)

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f
```

Остановка:

```bash
docker compose down
```

## 4. Что проверять по ТЗ

### Основной функционал
- `GET /item/<id>/` — HTML товара + кнопка Buy
- `GET /buy/<id>/` — JSON с `session.id`

Проверка:

```bash
curl -X GET http://127.0.0.1:8000/buy/1/
```

Ожидаемо:

```json
{"id":"cs_test_..."}
```

Открыть в браузере:

```text
http://127.0.0.1:8000/item/1/
```

Нажать `Buy` — редирект в Stripe Checkout.

Тестовая карта Stripe:
- `4242 4242 4242 4242`
- любая будущая дата
- любой CVC

### Бонусы
- `GET /order/<id>/` + `GET /buy-order/<id>/`
- `Discount` и `Tax` через админку
- `Item.currency` (`USD` / `RUB`) и выбор keypair по валюте
- `GET /buy-intent/<id>/`

## 5. Что должно быть в `.env` и `.env.example`

### `.env.example` (в репозитории)
Только шаблон, без секретов:

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
DOMAIN_URL=http://127.0.0.1:8000

STRIPE_DEFAULT_CURRENCY=usd
STRIPE_SECRET_KEY_USD=sk_test_replace_with_real_key
STRIPE_PUBLISHABLE_KEY_USD=pk_test_replace_with_real_key
STRIPE_SECRET_KEY_RUB=sk_test_replace_with_real_key
STRIPE_PUBLISHABLE_KEY_RUB=pk_test_replace_with_real_key
```

### `.env` (локально/на сервере, не коммитить)
Реальные значения:

```env
DJANGO_SECRET_KEY=your-real-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
DOMAIN_URL=http://127.0.0.1:8000

STRIPE_DEFAULT_CURRENCY=usd
STRIPE_SECRET_KEY_USD=sk_test_real_value
STRIPE_PUBLISHABLE_KEY_USD=pk_test_real_value
STRIPE_SECRET_KEY_RUB=sk_test_real_value_or_second_pair
STRIPE_PUBLISHABLE_KEY_RUB=pk_test_real_value_or_second_pair
```

## 6. Вопрос про Stripe ключи

Для тестового задания использовать **test keys**:
- `sk_test_...`
- `pk_test_...`

`live` ключи не нужны.
Если ключи где-то опубликованы, их нужно перевыпустить (rotate).
