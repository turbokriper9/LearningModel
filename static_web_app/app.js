// Демонстрационный скрипт для статической версии приложения
function showTab(tabName) {
    // Скрываем все вкладки
    const tabs = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].style.display = 'none';
    }
    
    // Показываем выбранную вкладку
    document.getElementById(tabName + '-tab').style.display = 'block';
    
    // Обновляем активную кнопку
    const buttons = document.querySelector('.tabs').getElementsByTagName('button');
    for (let i = 0; i < buttons.length; i++) {
        if (buttons[i].onclick.toString().includes(tabName)) {
            buttons[i].classList.add('active');
        } else {
            buttons[i].classList.remove('active');
        }
    }
}

// Функция для демонстрационного обновления счетчика
function updateDemoCount() {
    // Генерируем случайное число от 15 до 30
    const randomCount = Math.floor(Math.random() * 16) + 15;
    
    // Обновляем счетчик
    const counter = document.getElementById('counter');
    counter.textContent = randomCount;
    
    // Обновляем подпись
    const label = counter.nextElementSibling;
    if (randomCount === 1) {
        label.textContent = 'студент';
    } else if (randomCount >= 2 && randomCount <= 4) {
        label.textContent = 'студента';
    } else {
        label.textContent = 'студентов';
    }
    
    // Добавляем анимацию
    counter.classList.add('updated');
    setTimeout(() => {
        counter.classList.remove('updated');
    }, 500);
}

// Автоматическое обновление счетчика каждые 10 секунд
setInterval(updateDemoCount, 10000);

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    updateDemoCount();
});
