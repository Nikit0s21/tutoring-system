console.log('JavaScript подключен!');

document.querySelectorAll('.day-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        alert('Вкладка дня работает! Дата: ' + this.dataset.date);
    });
});