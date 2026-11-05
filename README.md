# Kiti Toys Shop Bot

Демонстрационный Telegram-бот для вымышленного магазина кошачьих игрушек. Проект создан в качестве портфолио и показывает пример интеграции Telegram Bot API с PostgreSQL.

Покупатели могут просматривать каталог, добавлять товары в корзину и оформлять заказы. Администраторы управляют каталогом и обрабатывают поступающие заказы.

## Возможности

### Покупатель

- Просмотр категорий и каталога товаров.
- Просмотр карточек товаров с описанием, ценой и фотографией (если она добавлена).
- Добавление товаров в корзину.
- Просмотр и очистка корзины.
- Оформление заказа.

### Администратор

- Просмотр поступивших заказов и их состава.
- Изменение статуса заказа.
- Создание, переименование и удаление категорий.
- Добавление товаров.
- Редактирование карточек товаров.
- Удаление товаров.

Доступ к административным функциям предоставляется пользователям, Telegram ID которых указан в `ADMIN_IDS`.

## Технологии

- **Python 3.12** — язык программирования.
- **PostgreSQL 16** — хранение данных.
- **python-telegram-bot** — взаимодействие с Telegram Bot API.
- **asyncpg** — асинхронная работа с PostgreSQL.
- **python-dotenv** — загрузка настроек из `.env`.
- **systemd** — пример запуска бота в качестве системной службы Linux.

## Структура проекта

```text
kiti-toys-shop-bot/
├── core/
│   ├── config.py          # Загрузка и проверка настроек
│   ├── db.py              # Подключение к PostgreSQL и пул соединений
│   ├── formatting.py      # Форматирование цен, товаров, корзины и заказов
│   ├── repository.py      # Операции чтения и изменения данных
│   └── texts.py           # Тексты сообщений бота
├── deploy/
│   └── shop-bot.service   # Пример systemd-службы
├── sql/
│   ├── migrations/        # SQL-миграции
│   ├── queries.sql        # SQL-запросы проекта
│   ├── schema.sql         # Начальная структура базы данных
│   └── seed.sql           # Демонстрационные данные
├── tg_bot/
│   ├── admin.py           # Обработчики административных функций
│   ├── bot.py             # Сборка и запуск Telegram-приложения
│   ├── handlers.py        # Обработчики пользовательских действий
│   └── keyboards.py       # Клавиатуры Telegram
├── .env.example           # Шаблон переменных окружения
├── .gitignore
├── main.py                # Точка входа
└── requirements.txt       # Зависимости Python
```

## Скриншоты
markdown
![Главное меню](screenshots/main-menu.png)
![Каталог товаров](screenshots/catalog.png)
![Корзина](screenshots/basket.png)
![Карточка товара](screenshots/cart.png)
![Панель администратора](screenshots/admin-panel.png)
![Заказ](screenshots/order.png)

## Требования

- Linux или другая система, на которой доступны Python и PostgreSQL.
- Python 3.12.
- PostgreSQL 16.
- Telegram-бот и его токен, полученный у [@BotFather](https://t.me/BotFather).

Ниже приведены инструкции для Linux и Windows. Для Windows команды рассчитаны на PowerShell.

## Установка

Клонируйте репозиторий:

```bash
git clone https://github.com/MiGayChen/kiti-toys-shop-bot.git
cd kiti-toys-shop-bot
```

Создайте виртуальное окружение и установите зависимости:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Создайте файл настроек:

```bash
cp .env.example .env
```

### Установка в Windows

1. Установите **Python 3.12** с официального сайта [python.org](https://www.python.org/downloads/). Во время установки отметьте пункт **Add Python to PATH**.
2. Установите **PostgreSQL 16** с [официальной страницы загрузки](https://www.postgresql.org/download/windows/). Запомните пароль пользователя `postgres`, который задаётся установщиком.
3. Установите Git для Windows, если планируете клонировать репозиторий командой `git`.
4. Откройте PowerShell и перейдите в каталог, где хотите разместить проект. Выполните:

```powershell
git clone https://github.com/MiGayChen/kiti-toys-shop-bot.git
cd kiti-toys-shop-bot
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Если команда `git` недоступна, можно скачать ZIP-архив репозитория с GitHub, распаковать его и открыть PowerShell в получившейся папке проекта. Остальные команды выполняются так же.

После установки зависимостей настройте `.env` и базу данных по следующим разделам. Для запуска в Windows используйте:

```powershell
.\.venv\Scripts\python.exe main.py
```

Окно PowerShell должно оставаться открытым, пока бот работает. Для остановки нажмите `Ctrl+C`. Это обычный запуск процесса, а не установка фоновой службы Windows.

## Настройка

Откройте `.env` и укажите параметры:

| Переменная | Назначение |
|---|---|
| `BOT_TOKEN` | Токен Telegram-бота, полученный у @BotFather |
| `DATABASE_URL` | Строка подключения к PostgreSQL |
| `OWNER_ID` | Telegram ID пользователя, которому отправляются уведомления о новых заказах |
| `ADMIN_IDS` | Telegram ID администраторов через запятую |
| `SHOP_TIMEZONE` | Часовой пояс магазина, например `Asia/Almaty` |

Пример строки подключения к PostgreSQL:

```env
DATABASE_URL=postgresql://kiti_toys_role:YOUR_PASSWORD@localhost:5432/kiti_toys_base
```

`ADMIN_IDS` может содержать несколько ID, разделённых запятыми. Если переменная пустая, административные обработчики не подключаются. Если `OWNER_ID` не задан или равен `0`, уведомления владельцу о новых заказах не отправляются.

**Не публикуйте файл `.env` и не добавляйте в репозиторий токен бота, пароли или другие секреты.** Файл `.env` уже указан в `.gitignore`.

## Настройка базы данных

Создайте роль и базу данных от имени администратора PostgreSQL. Вместо `YOUR_PASSWORD` укажите собственный пароль:

```bash
sudo -u postgres psql -c "CREATE ROLE kiti_toys_role LOGIN PASSWORD 'YOUR_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE kiti_toys_base OWNER kiti_toys_role;"
```

Создайте таблицы и остальные объекты базы данных:

```bash
psql -h localhost -U kiti_toys_role -d kiti_toys_base -f sql/schema.sql
```

### Создание базы данных в Windows

Можно использовать **pgAdmin**, который устанавливается вместе с PostgreSQL, или приложение **SQL Shell (psql)**. Подключитесь к серверу PostgreSQL пользователем `postgres` и выполните SQL-команды (замените пароль на свой):

```sql
CREATE ROLE kiti_toys_role LOGIN PASSWORD 'YOUR_PASSWORD';
CREATE DATABASE kiti_toys_base OWNER kiti_toys_role;
```

Затем откройте PowerShell в папке проекта и выполните команду для создания таблиц:

```powershell
psql -h localhost -U kiti_toys_role -d kiti_toys_base -f sql/schema.sql
```

При запросе введите пароль роли `kiti_toys_role`. Если PowerShell сообщает, что `psql` не найден, запустите **SQL Shell (psql)** из меню «Пуск» либо добавьте каталог `bin` установленного PostgreSQL в `PATH`.

При необходимости добавьте демонстрационные данные:

```bash
psql -h localhost -U kiti_toys_role -d kiti_toys_base -f sql/seed.sql
```

`seed.sql` предназначен для пустой базы данных. Повторный запуск скрипта не предназначен для обновления уже заполненной базы.

После создания базы укажите соответствующую строку подключения в `DATABASE_URL`.

В исходной инструкции проекта предполагается, что PostgreSQL принимает локальные подключения через `127.0.0.1`.

## Запуск

После настройки `.env` и базы данных запустите:

```bash
.venv/bin/python main.py
```

## Запуск через systemd

В репозитории есть пример службы `deploy/shop-bot.service`. Для установки службы с каталогом проекта `/opt/shop-bot` выполните:

```bash
sudo useradd --system --home-dir /opt/shop-bot --shell /usr/sbin/nologin shopbot
sudo chown -R shopbot:shopbot /opt/shop-bot
sudo chmod 600 /opt/shop-bot/.env
sudo cp deploy/shop-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now shop-bot
```

Проверить состояние и просмотреть логи можно командами:

```bash
systemctl status shop-bot
journalctl -u shop-bot -f
```

## Обновление

Если бот установлен как systemd-служба:

```bash
sudo systemctl stop shop-bot
cd /opt/shop-bot
sudo chown -R "$USER": .
git pull
.venv/bin/pip install -r requirements.txt
sudo chown -R shopbot:shopbot .
sudo chmod 600 .env
sudo systemctl start shop-bot
```

Перед обновлением рабочей базы данных рекомендуется сделать резервную копию. SQL-файлы из `sql/migrations/` следует применять осознанно: не запускайте миграции повторно без проверки их назначения и текущего состояния базы.

## Тестирование

В локальной среде разработчика был выполнен запуск:

```bash
python -m pytest -v
```

Результат последнего предоставленного прогона: **5 тестов пройдены**. Они проверяют разбор и форматирование цены, форматирование суммы корзины и отображение времени заказа с часовым поясом магазина.

Тестовые файлы не входят в приложенный архив исходного проекта. Чтобы результаты тестирования можно было воспроизвести после клонирования репозитория, добавьте тесты в репозиторий вместе с README.

## Лицензия

Лицензия проекта пока не указана.
