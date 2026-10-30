# Демо-бот магазина кошачьих игрушек (Telegram)

Бот на Python и PostgreSQL: каталог, корзина, оформление заказа, панель администратора.
Ядро `core/` не знает про Telegram, поэтому на нём можно строить боты для VK и Discord.

## Требования

- Python 3.12, PostgreSQL 16
- токен бота от @BotFather

## Установка

```
sudo mkdir /opt/shop-bot
sudo chown "$USER": /opt/shop-bot
git clone git@github.com:MiGayChen/kiti-toys-shop-bot.git /opt/shop-bot
cd /opt/shop-bot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`:

- `BOT_TOKEN` токен бота
- `DATABASE_URL` строка подключения к PostgreSQL
- `OWNER_ID` id в Telegram, кому приходят уведомления о заказах
- `ADMIN_IDS` id админов через запятую (если пусто, админка выключена)
- `SHOP_TIMEZONE` часовой пояс магазина, например `Asia/Almaty`

## База данных

Роль и база создаются от имени администратора PostgreSQL (пароль подставьте свой):

```
sudo -u postgres psql -c "CREATE ROLE kiti_toys_role LOGIN PASSWORD 'ПАРОЛЬ';"
sudo -u postgres psql -c "CREATE DATABASE kiti_toys_base OWNER kiti_toys_role;"
psql -h localhost -U kiti_toys_role -d kiti_toys_base -f sql/schema.sql
```

Тестовые данные (только в пустую базу, команда очищает таблицы товаров):

```
psql -h localhost -U kiti_toys_role -d kiti_toys_base -f sql/seed.sql
```

PostgreSQL должен слушать только 127.0.0.1.

## Запуск

```
.venv/bin/python main.py tg
```

## Запуск как сервис (systemd)

```
sudo useradd --system --home-dir /opt/shop-bot --shell /usr/sbin/nologin shopbot
sudo chown -R shopbot:shopbot /opt/shop-bot
sudo chmod 600 /opt/shop-bot/.env
sudo cp deploy/shop-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now shop-bot
```

Состояние и логи:

```
systemctl status shop-bot
journalctl -u shop-bot -f
```

## Обновление

```
sudo systemctl stop shop-bot
cd /opt/shop-bot
sudo chown -R "$USER": .
git pull
.venv/bin/pip install -r requirements.txt
sudo chown -R shopbot:shopbot .
sudo chmod 600 .env
sudo systemctl start shop-bot
```
