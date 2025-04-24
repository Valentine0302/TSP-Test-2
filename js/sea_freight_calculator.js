// JavaScript для интеграции с API калькулятора морских ставок
document.addEventListener('DOMContentLoaded', function() {
    const seaFreightForm = document.getElementById('seaFreightForm');
    const calculationSpinner = document.getElementById('calculationSpinner');
    const resultsContainer = document.getElementById('resultsContainer');
    const carrierTableBody = document.getElementById('carrierTableBody');
    const backToFormButton = document.getElementById('backToFormButton');
    const alertContainer = document.getElementById('alertContainer');
    
    // API URL
    const API_BASE_URL = '../api/run/sea_freight_api.py';
    
    // Обработчик отправки формы
    seaFreightForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Показываем спиннер загрузки
        calculationSpinner.style.display = 'block';
        
        // Собираем данные формы
        const formData = {
            origin: document.getElementById('origin').value,
            destination: document.getElementById('destination').value,
            cargoType: document.getElementById('cargoType').value,
            containerType: document.getElementById('containerType').value,
            weight: document.getElementById('weight').value,
            volume: document.getElementById('volume').value,
            goodsValue: document.getElementById('goodsValue').value,
            deliveryDate: document.getElementById('deliveryDate').value,
            incoterms: document.getElementById('incoterms').value,
            dangerous: document.getElementById('dangerous').value,
            insurance: document.getElementById('insurance').value,
            customs: document.getElementById('customs').value,
            additionalInfo: document.getElementById('additionalInfo').value,
            name: document.getElementById('name').value,
            company: document.getElementById('company').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value
        };
        
        // Сначала проверяем email
        fetch(`${API_BASE_URL}/api/sea-freight/verify-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: formData.email })
        })
        .then(response => response.json())
        .then(data => {
            // Если email уже верифицирован, отправляем запрос на расчет
            if (data.verified) {
                calculateRates(formData);
            } else {
                // Автоматическая верификация email
                verifyEmailAutomatically(formData);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Произошла ошибка при проверке email. Пожалуйста, попробуйте еще раз.', 'danger');
            calculationSpinner.style.display = 'none';
        });
    });
    
    // Функция для автоматической верификации email
    function verifyEmailAutomatically(formData) {
        // Здесь происходит автоматическая верификация email
        // В реальной системе здесь будет проверка MX-записей, фильтрация временных доменов и т.д.
        
        // Имитируем успешную верификацию и отправляем запрос на расчет
        setTimeout(() => {
            calculateRates(formData);
        }, 1000);
    }
    
    // Функция для расчета ставок
    function calculateRates(formData) {
        fetch(`${API_BASE_URL}/api/sea-freight/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Произошла ошибка при расчете ставок');
                });
            }
            return response.json();
        })
        .then(data => {
            // Скрываем спиннер загрузки
            calculationSpinner.style.display = 'none';
            
            // Отображаем результаты
            displayResults(data.results);
            
            // Скрываем форму и показываем результаты
            seaFreightForm.parentElement.style.display = 'none';
            resultsContainer.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert(error.message, 'danger');
            calculationSpinner.style.display = 'none';
        });
    }
    
    // Функция для отображения результатов
    function displayResults(results) {
        // Очищаем таблицу
        carrierTableBody.innerHTML = '';
        
        // Сортируем результаты по стоимости (от меньшей к большей)
        results.sort((a, b) => a.cost - b.cost);
        
        // Добавляем строки в таблицу
        results.forEach((result, index) => {
            const row = document.createElement('tr');
            
            // Отмечаем лучшую ставку
            if (index === 0) {
                row.classList.add('best-rate');
            }
            
            row.innerHTML = `
                <td>${result.carrier}</td>
                <td>$${result.cost.toFixed(2)}</td>
                <td>${result.transit_time} дней</td>
                <td>${index === 0 ? 'Лучшая цена' : ''}</td>
            `;
            
            carrierTableBody.appendChild(row);
        });
    }
    
    // Обработчик кнопки "Вернуться к форме"
    backToFormButton.addEventListener('click', function() {
        resultsContainer.style.display = 'none';
        seaFreightForm.parentElement.style.display = 'block';
    });
    
    // Функция для отображения уведомлений
    function showAlert(message, type) {
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;
        
        // Автоматически скрываем уведомление через 5 секунд
        setTimeout(() => {
            alertContainer.innerHTML = '';
        }, 5000);
    }
});
