# Руководство по развертыванию SMM Agents

Подробное руководство по развертыванию системы модерации и публикации новостей в различных окружениях.

## 📋 Предварительные требования

### Системные требования
- **Python**: 3.12+
- **UV**: последняя версия
- **Docker**: 20.10+ (опционально)
- **Docker Compose**: 2.0+ (опционально)
- **ОС**: Linux, macOS, Windows с WSL2

### Подготовка Telegram ботов

1. **Создание бота модератора:**
   - Откройте [@BotFather](https://t.me/BotFather)
   - Выполните `/newbot`
   - Укажите имя: `YourProject Moderator Bot`
   - Укажите username: `yourproject_moderator_bot`
   - Сохраните токен

2. **Создание бота издателя:**
   - Повторите процесс для издателя
   - Имя: `YourProject Publisher Bot`
   - Username: `yourproject_publisher_bot`
   - Сохраните токен

3. **Настройка канала:**
   - Создайте канал для публикации новостей
   - Добавьте бота издателя как администратора
   - Предоставьте права на публикацию сообщений
   - Получите ID канала (начинается с `@` или `-100`)

## 🛠 Локальное развертывание

### 1. Подготовка окружения

```bash
# Клонирование репозитория
git clone <repository-url>
cd smm-agents

# Установка UV (если не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # или ~/.zshrc

# Проверка установки
uv --version
```

### 2. Автоматическая установка

```bash
# Выполнение скрипта установки
chmod +x scripts/setup.sh
./scripts/setup.sh
```

Скрипт автоматически:
- Установит зависимости
- Создаст структуру директорий
- Инициализирует базу данных
- Применит миграции
- Создаст .env файл

### 3. Ручная настройка

```bash
# Установка зависимостей
uv sync

# Создание .env файла
cp .env.example .env

# Редактирование конфигурации
nano .env
```

Настройте следующие обязательные параметры:
```env
MODERATOR_BOT_TOKEN=7654803812:AAGiiNZn_hHFMriOheh4N5xUL2odFU3NRl0
PUBLISHER_BOT_TOKEN=8169955910:AAHyds5lwbLpafuBwl4jOdsY6Fd4l_4bSpU
CHANNEL_ID=@your_news_channel
```

### 4. Инициализация базы данных

```bash
# Создание таблиц
uv run python -c "
import asyncio
from src.database.database import engine, Base
from src.database.models import User, News

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ База данных инициализирована')

asyncio.run(init_db())
"

# Применение миграций
uv run alembic upgrade head
```

### 5. Запуск системы

```bash
# Запуск системы ботов
uv run python scripts/run_system.py

# Или запуск отдельных компонентов
uv run python src/main.py  # Сбор новостей
```

## 🐳 Docker развертывание

### 1. Подготовка конфигурации

```bash
# Создание .env файла
cp .env.example .env

# Настройка для Docker (PostgreSQL)
cat >> .env << EOF
DATABASE_URL=postgresql+asyncpg://smm_user:smm_password@db:5432/smm_agents
DB_USER=smm_user
DB_PASSWORD=your_secure_password
ENVIRONMENT=production
EOF
```

### 2. Развертывание с PostgreSQL

```bash
# Запуск полного стека
cd docker
docker-compose up --build -d

# Проверка состояния
docker-compose ps

# Просмотр логов
docker-compose logs -f app
```

### 3. Развертывание только приложения (SQLite)

```bash
# Сборка образа
docker build -f docker/Dockerfile -t smm-agents .

# Запуск с SQLite
docker run -d \
  --name smm-agents \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/telegram_bot.db:/app/telegram_bot.db \
  --restart unless-stopped \
  smm-agents
```

### 4. Настройка reverse proxy (Nginx)

```nginx
# /etc/nginx/sites-available/smm-agents
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /adminer {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🌐 Производственное развертывание

### 1. Подготовка сервера

```bash
# Обновление системы (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагрузка для применения изменений
sudo reboot
```

### 2. Настройка окружения

```bash
# Создание пользователя для приложения
sudo useradd -m -s /bin/bash smm-agents
sudo usermod -aG docker smm-agents

# Переключение на пользователя
sudo su - smm-agents

# Клонирование репозитория
git clone <repository-url>
cd smm-agents
```

### 3. Production конфигурация

```bash
# Создание production .env
cat > .env << EOF
# Production Configuration
ENVIRONMENT=production

# Telegram Bots
MODERATOR_BOT_TOKEN=your_production_moderator_token
PUBLISHER_BOT_TOKEN=your_production_publisher_token
CHANNEL_ID=@your_production_channel

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://smm_user:$(openssl rand -base64 32)@db:5432/smm_agents
DB_USER=smm_user
DB_PASSWORD=$(openssl rand -base64 32)

# Security
LOG_LEVEL=WARNING
PUBLISH_INTERVAL_SECONDS=600

# Optional services
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
FLOWISE_HOST=https://your-flowise-instance.com
FLOWISE_ID=your_flowise_flow_id
EOF

# Защита конфигурации
chmod 600 .env
```

### 4. Настройка systemd сервиса

```bash
# Создание systemd unit файла
sudo tee /etc/systemd/system/smm-agents.service << EOF
[Unit]
Description=SMM Agents News Moderation System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/smm-agents/smm-agents/docker
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=smm-agents
Group=smm-agents

[Install]
WantedBy=multi-user.target
EOF

# Активация сервиса
sudo systemctl daemon-reload
sudo systemctl enable smm-agents
sudo systemctl start smm-agents
```

### 5. Настройка мониторинга

```bash
# Создание скрипта мониторинга
cat > /home/smm-agents/monitor.sh << 'EOF'
#!/bin/bash

CONTAINER_NAME="smm-agents"
LOG_FILE="/home/smm-agents/monitor.log"

check_container() {
    if ! docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo "$(date): Container ${CONTAINER_NAME} is not running. Restarting..." >> ${LOG_FILE}
        cd /home/smm-agents/smm-agents/docker
        docker-compose restart app
        echo "$(date): Container restarted" >> ${LOG_FILE}
    fi
}

check_container
EOF

chmod +x /home/smm-agents/monitor.sh

# Добавление в crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/smm-agents/monitor.sh") | crontab -
```

### 6. Настройка резервного копирования

```bash
# Скрипт резервного копирования
cat > /home/smm-agents/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/smm-agents/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p ${BACKUP_DIR}

# Бэкап базы данных PostgreSQL
docker-compose exec -T db pg_dump -U smm_user smm_agents > ${BACKUP_DIR}/db_backup_${DATE}.sql

# Бэкап логов
tar -czf ${BACKUP_DIR}/logs_backup_${DATE}.tar.gz logs/

# Удаление старых бэкапов (старше 30 дней)
find ${BACKUP_DIR} -name "*.sql" -mtime +30 -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +30 -delete

echo "$(date): Backup completed: ${DATE}" >> /home/smm-agents/backup.log
EOF

chmod +x /home/smm-agents/backup.sh

# Добавление в crontab (ежедневно в 2:00)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/smm-agents/backup.sh") | crontab -
```

## 🔧 Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Мониторинг и логирование

### 1. Настройка Grafana + Prometheus (опционально)

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - smm-network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - smm-network

networks:
  smm-network:
    external: true
```

### 2. Настройка алертов

```bash
# Создание скрипта проверки здоровья
cat > /home/smm-agents/health_check.sh << 'EOF'
#!/bin/bash

WEBHOOK_URL="your_slack_webhook_or_telegram_bot"

# Проверка контейнера
if ! docker ps --format "table {{.Names}}" | grep -q "smm-agents"; then
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"🚨 SMM Agents container is down!"}' \
        ${WEBHOOK_URL}
fi

# Проверка места на диске
DISK_USAGE=$(df /home/smm-agents | tail -1 | awk '{print $5}' | sed 's/%//')
if [ ${DISK_USAGE} -gt 90 ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"⚠️ Disk usage is above 90%: '${DISK_USAGE}'%"}' \
        ${WEBHOOK_URL}
fi
EOF

chmod +x /home/smm-agents/health_check.sh

# Добавление в crontab (каждые 15 минут)
(crontab -l 2>/dev/null; echo "*/15 * * * * /home/smm-agents/health_check.sh") | crontab -
```

## 🐛 Устранение неполадок

### Проблемы с Docker

```bash
# Проверка статуса
docker-compose ps

# Перезапуск сервисов
docker-compose restart

# Проверка логов
docker-compose logs -f app
docker-compose logs -f db

# Полная перезагрузка
docker-compose down -v
docker-compose up --build -d
```

### Проблемы с базой данных

```bash
# Подключение к PostgreSQL контейнеру
docker-compose exec db psql -U smm_user -d smm_agents

# Проверка таблиц
\dt

# Проверка подключений
SELECT * FROM pg_stat_activity;
```

### Проблемы с ботами

```bash
# Проверка токенов
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# Проверка webhook'ов (если используются)
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo

# Сброс webhook'ов
curl https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```yaml
# docker-compose.scale.yml
services:
  app:
    # ... конфигурация приложения
    deploy:
      replicas: 3
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
```

### Вертикальное масштабирование

```yaml
services:
  app:
    # ... конфигурация
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## 🔐 Безопасность

### Настройка файрвола

```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp  # PostgreSQL только внутри Docker сети
```

### Ротация секретов

```bash
# Создание скрипта ротации
cat > /home/smm-agents/rotate_secrets.sh << 'EOF'
#!/bin/bash

# Генерация нового пароля БД
NEW_PASSWORD=$(openssl rand -base64 32)

# Обновление .env
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=${NEW_PASSWORD}/" .env
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${NEW_PASSWORD}/" .env

# Перезапуск с новыми секретами
docker-compose down
docker-compose up -d

echo "$(date): Secrets rotated" >> /home/smm-agents/security.log
EOF

chmod +x /home/smm-agents/rotate_secrets.sh

# Ротация каждый месяц
(crontab -l 2>/dev/null; echo "0 3 1 * * /home/smm-agents/rotate_secrets.sh") | crontab -
```

## 🌐 Доступ к сервисам

После успешного развертывания вы можете получить доступ к:

- **Приложение**: http://localhost:8000
- **Adminer** (веб-интерфейс БД): http://localhost:8081
- **PostgreSQL**: localhost:5432

### Подключение к Adminer

1. Откройте http://localhost:8081
2. Выберите "PostgreSQL"
3. Введите данные:
   - **Сервер**: db
   - **Пользователь**: smm_user
   - **Пароль**: смотрите в .env файле
   - **База данных**: smm_agents

Теперь у вас есть полное руководство по развертыванию SMM Agents системы в любом окружении! 