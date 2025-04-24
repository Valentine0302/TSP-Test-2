#!/bin/bash

# Установка зависимостей
pip install flask flask-cors requests

# Создание директории для запуска
mkdir -p /home/ubuntu/tsp_website/api/run

# Копирование API в директорию запуска
cp /home/ubuntu/tsp_website/api/sea_freight_api.py /home/ubuntu/tsp_website/api/run/

# Создание скрипта запуска
cat > /home/ubuntu/tsp_website/api/run/start_api.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 sea_freight_api.py
EOF

# Делаем скрипт запуска исполняемым
chmod +x /home/ubuntu/tsp_website/api/run/start_api.sh

# Создание README с инструкциями
cat > /home/ubuntu/tsp_website/api/README.md << 'EOF'
# Калькулятор морских ставок - API

## Установка и запуск

1. Установите необходимые зависимости:
   ```
   pip install flask flask-cors requests
   ```

2. Перейдите в директорию запуска:
   ```
   cd /home/ubuntu/tsp_website/api/run
   ```

3. Запустите API:
   ```
   ./start_api.sh
   ```

API будет доступно по адресу: http://localhost:5000

## Эндпоинты API

### 1. Расчет морских ставок
- URL: `/api/sea-freight/calculate`
- Метод: POST
- Тело запроса: JSON с данными формы
- Ответ: JSON с результатами расчета

### 2. Верификация email
- URL: `/api/sea-freight/verify-email`
- Метод: POST
- Тело запроса: JSON с email
- Ответ: JSON с результатом верификации

### 3. Подтверждение верификации
- URL: `/api/sea-freight/confirm-verification`
- Метод: POST
- Тело запроса: JSON с email и кодом
- Ответ: JSON с результатом подтверждения

### 4. История расчетов
- URL: `/api/sea-freight/history`
- Метод: GET
- Параметры: email
- Ответ: JSON с историей расчетов

## Интеграция с фронтендом

Фронтенд уже настроен для работы с API. Для корректной работы необходимо:

1. Запустить API
2. Открыть страницу калькулятора в браузере: `/calculation/sea_freight.html`

## Примечания по развертыванию

В продакшен-среде необходимо:

1. Настроить HTTPS для безопасной передачи данных
2. Настроить реальную отправку email для верификации
3. Настроить прокси-сервер (например, Nginx) для перенаправления запросов к API
4. Обновить URL API в файле sea_freight.html
EOF

# Создание архива с готовым продуктом
cd /home/ubuntu
zip -r sea_freight_calculator_complete.zip tsp_website/calculation/sea_freight.html tsp_website/api/

echo "Установка завершена. Для запуска API выполните:"
echo "cd /home/ubuntu/tsp_website/api/run && ./start_api.sh"
