document.addEventListener('DOMContentLoaded', function() {
    // Элементы интерфейса
    const dayTabs = document.querySelectorAll('.day-tab');
    const dayContents = document.querySelectorAll('.day-content');
    const timeSlots = document.querySelectorAll('.time-slot');
    const submitBtn = document.getElementById('submit-btn');
    const selectedTimeInput = document.getElementById('selected-time');

    // Показывает выбранный день
    function showDay(date) {
        // Скрываем все содержимое дней
        dayContents.forEach(content => {
            content.style.display = 'none';
        });

        // Показываем выбранный день
        const activeDay = document.getElementById(`day-${date}`);
        if (activeDay) {
            activeDay.style.display = 'block';
        }

        // Обновляем активные вкладки
        dayTabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.date === date);
        });
    }

    // Выбирает временной слот
    function selectTimeSlot(slot) {
        if (slot.classList.contains('booked')) return;

        // Снимаем выделение со всех слотов
        timeSlots.forEach(s => {
            s.classList.remove('selected');
        });

        // Выделяем текущий слот
        slot.classList.add('selected');

        // Заполняем скрытое поле
        selectedTimeInput.value = slot.dataset.start;

        // Активируем кнопку
        submitBtn.disabled = false;

        // Плавная прокрутка к кнопке подтверждения
        submitBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Добавляем обработчики событий

    // Для вкладок дней
    dayTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Анимация нажатия
            this.style.transform = 'translateY(2px)';
            setTimeout(() => {
                this.style.transform = this.classList.contains('active')
                    ? 'translateY(-2px)'
                    : '';
            }, 100);

            showDay(this.dataset.date);
        });
    });

    // Для слотов времени
    timeSlots.forEach(slot => {
        slot.addEventListener('click', function() {
            // Анимация нажатия
            if (!this.classList.contains('booked')) {
                this.style.transform = 'translateY(2px)';
                setTimeout(() => {
                    this.style.transform = this.classList.contains('selected')
                        ? 'translateY(-2px)'
                        : '';
                }, 100);
            }

            selectTimeSlot(this);
        });
    });

    // Показываем первый день по умолчанию
    if (dayTabs.length > 0) {
        showDay(dayTabs[0].dataset.date);
    }

    // Добавляем эффект при наведении на кнопку
    if (submitBtn) {
        submitBtn.addEventListener('mouseenter', function() {
            if (!this.disabled) {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.15)';
            }
        });

        submitBtn.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Обработка клика по ссылке деталей программы
    document.querySelectorAll('.program-detail-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (e.target !== this) {
                e.stopPropagation();
                window.open(this.href, '_blank');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Автоматически раскрываем выбранную программу
    const radioInputs = document.querySelectorAll('input[name="program"]');
    radioInputs.forEach(radio => {
        radio.addEventListener('change', function() {
            const programId = this.value;
            const accordionItem = this.closest('.accordion-item');
            const collapseElement = accordionItem.querySelector('.accordion-collapse');

            // Закрываем все другие аккордеоны
            document.querySelectorAll('.accordion-collapse').forEach(el => {
                if (el !== collapseElement) {
                    bootstrap.Collapse.getInstance(el)?.hide();
                }
            });

            // Открываем текущий
            if (!collapseElement.classList.contains('show')) {
                new bootstrap.Collapse(collapseElement, { toggle: true });
            }
        });
    });

    // Ограничиваем высоту описания и добавляем скролл
    const descriptions = document.querySelectorAll('.program-description');
    descriptions.forEach(desc => {
        if (desc.scrollHeight > desc.clientHeight) {
            desc.style.border = '1px solid #dee2e6';
            desc.style.padding = '8px';
        }
    });
});