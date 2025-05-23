class TutorReports {
    constructor(userId) {
        this.userId = userId;
        this.charts = {
            revenue: null,
            popularity: null
        };

        this.elements = {
            loading: document.getElementById('loading-indicator'),
            error: document.getElementById('error-message'),
            content: document.getElementById('reports-content'),
            rangeButtons: document.querySelectorAll('.range-btn'),
            completedLessons: document.getElementById('completed-lessons'),
            canceledLessons: document.getElementById('canceled-lessons'),
            fillRate: document.getElementById('fill-rate'),
            revenueCanvas: document.getElementById('revenue-chart'),
            popularityCanvas: document.getElementById('popularity-chart')
        };

        // Если canvas элементы не найдены, прекращаем инициализацию
        if (!this.elements.revenueCanvas || !this.elements.popularityCanvas) {
            console.error('Canvas elements not found');
            return;
        }

        // Установка оптимального размера canvas
        this.setCanvasSize(this.elements.revenueCanvas);
        this.setCanvasSize(this.elements.popularityCanvas);

        this.initEventListeners();
        this.loadReports(); // Первоначальная загрузка
    }

    setCanvasSize(canvas) {
        // Устанавливаем размеры canvas в зависимости от ширины экрана
        const parentWidth = canvas.parentElement.clientWidth;
        canvas.width = parentWidth;
        canvas.height = Math.min(300, parentWidth * 0.5); // Максимальная высота 300px
    }

    initEventListeners() {
        this.elements.rangeButtons.forEach(btn => {
            btn.addEventListener('click', () => this.handleRangeChange(btn));
        });
    }

    handleRangeChange(btn) {
        this.elements.rangeButtons.forEach(b => {
            b.classList.replace('btn-primary', 'btn-outline-primary');
        });
        btn.classList.replace('btn-outline-primary', 'btn-primary');
        this.loadReports(btn.dataset.range);
    }

    async loadReports(range = 'month') {
        try {
            this.showLoading();

            const response = await fetch(`/reports/api/tutor-reports/?range=${range}`);
            if (!response.ok) throw new Error(`Server error: ${response.status}`);

            const data = await response.json();
            if (!data) throw new Error('No data received');

            this.updateUI(data);

        } catch (error) {
            this.showError(`Ошибка загрузки: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    updateUI(data) {
        // Обновляем статистику
        if (data.lessons_stats) {
            this.elements.completedLessons.textContent = data.lessons_stats.completed || 0;
            this.elements.canceledLessons.textContent = data.lessons_stats.canceled || 0;
            this.elements.fillRate.textContent = `${data.lessons_stats.fill_rate || 0}%`;
        }

        // Обновляем графики
        if (data.program_revenue) {
            this.renderChart({
                name: 'revenue',
                canvas: this.elements.revenueCanvas,
                type: 'bar',
                data: {
                    labels: data.program_revenue.map(p => p.name),
                    datasets: [{
                        label: 'Доход (руб)',
                        data: data.program_revenue.map(p => p.total_revenue),
                        backgroundColor: '#4e73df',
                        barThickness: 'flex',
                        maxBarThickness: 50
                    }]
                },
                options: this.getChartOptions('Доход по программам')
            });
        }

        if (data.program_popularity) {
            this.renderChart({
                name: 'popularity',
                canvas: this.elements.popularityCanvas,
                type: 'doughnut',
                data: {
                    labels: data.program_popularity.map(p => p.name),
                    datasets: [{
                        data: data.program_popularity.map(p => p.popularity),
                        backgroundColor: [
                            '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e',
                            '#e74a3b', '#858796', '#f8f9fc', '#5a5c69'
                        ],
                        borderWidth: 1
                    }]
                },
                options: this.getChartOptions('Популярность программ')
            });
        }
    }

    getChartOptions(title) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 20
                    }
                },
                title: {
                    display: true,
                    text: title,
                    padding: {
                        top: 10,
                        bottom: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label || ''}: ${context.raw}`;
                        }
                    }
                }
            },
            layout: {
                padding: {
                    left: 10,
                    right: 10,
                    top: 10,
                    bottom: 10
                }
            }
        };
    }

    renderChart(config) {
        // Уничтожаем предыдущий график
        if (this.charts[config.name]) {
            this.charts[config.name].destroy();
            this.charts[config.name] = null;
        }

        // Очищаем canvas перед созданием нового графика
        const ctx = config.canvas.getContext('2d');
        ctx.clearRect(0, 0, config.canvas.width, config.canvas.height);

        // Создаем новый график
        try {
            this.charts[config.name] = new Chart(
                ctx,
                {
                    type: config.type,
                    data: config.data,
                    options: config.options
                }
            );
        } catch (error) {
            console.error(`Error rendering1 ${config.name} chart:`, error);
            this.showError(`Ошибка создания графика1: ${config.name}`);
        }
    }

    showLoading() {
        if (this.elements.loading) this.elements.loading.style.display = 'block';
        if (this.elements.content) this.elements.content.style.display = 'none';
        if (this.elements.error) this.elements.error.style.display = 'none';
    }

    hideLoading() {
        if (this.elements.loading) this.elements.loading.style.display = 'none';
        if (this.elements.content) this.elements.content.style.display = 'block';
    }

    showError(message) {
        if (this.elements.error) {
            this.elements.error.textContent = message;
            this.elements.error.style.display = 'block';
        }
        console.error(message);
    }
}

// Инициализация при полной загрузке страницы
window.addEventListener('DOMContentLoaded', () => {

    const defaultBtn = document.querySelector('.range-btn[data-range="week"]');
    if (defaultBtn) {
        defaultBtn.classList.replace('btn-outline-primary', 'btn-primary');
    }
});