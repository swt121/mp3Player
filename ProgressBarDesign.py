from tkinter import *


class CustomProgressBar(Canvas):
    def __init__(self, parent, width=300, height=10, bg_color="#404040", fg_color="#1DB954",
                 knob_color="#FFFFFF", knob_radius=8, border_width=0, command=None, **kwargs):
        """
        Инициализация кастомного прогресс-бара
        
        Args:
        parent: Родительский виджет, к которому привязывается Canvas;
        width: Ширина прогресс-бара;
        height: Высота прогресс-бара;
        bg_color: Цвет фона прогресс-бара;
        fg_color: Цвет заполненной части прогресс-бара;
        knob_color: Цвет ползунка;
        knob_radius: Радиус ползунка;
        border_width: Толщина рамки Canvas;
        command: Функция, вызываемая при изменении прогресса;
        kwargs: Дополнительные аргументы для Canvas.
        """
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0, **kwargs)

        # Сохранение параметров в атрибутах объекта
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.knob_color = knob_color
        self.knob_radius = knob_radius
        self.border_width = border_width
        self.command = command

        # Определение базовых параметров
        self.padding = 10  # Отступ по бокам
        self.progress_value = 0  # Начальное значение прогресса (в процентах)

        # Рисуем фоновую полосу прогресс-бара
        self.bg_bar = self.create_rounded_rect(self.padding, self.height // 2 - 3,
                                               self.width - self.padding, self.height // 2 + 3,
                                               radius=5, fill=self.bg_color, outline='')

        # Рисуем активную (заполненную) часть прогресс-бара
        self.fg_bar = self.create_rounded_rect(self.padding, self.height // 2 - 3,
                                               self.padding, self.height // 2 + 3,
                                               radius=5, fill=self.fg_color, outline='')

        # Рисуем ползунок
        self.knob = self.create_oval(self.padding - self.knob_radius, self.height // 2 - self.knob_radius,
                                     self.padding + self.knob_radius, self.height // 2 + self.knob_radius,
                                     fill=self.knob_color, outline='')

        # Переменная для отслеживания состояния перетаскивания ползунка
        self.dragging = False

        # Привязка событий для обработки кликов и перетаскивания ползунка
        self.bind_events()

    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        """
        Создает закругленный прямоугольник с указанными координатами и радиусом углов.

        Args:
        x1, y1, x2, y2: Координаты левой верхней и правой нижней точки;
        Radius: Радиус закругленных углов;
        Kwargs: Дополнительные аргументы для create_polygon.
        """
        points = [x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
                  x2, y1 + radius, x2, y2 - radius, x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2,
                  x1 + radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius,
                  x1, y1 + radius, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def bind_events(self):
        """Привязывает события для обработки кликов и перетаскивания ползунка"""
        self.tag_bind(self.knob, "<ButtonPress-1>", self.start_drag)  # Начало перетаскивания
        self.tag_bind(self.knob, "<ButtonRelease-1>", self.stop_drag)  # Окончание перетаскивания
        self.tag_bind(self.knob, "<B1-Motion>", self.on_drag)  # Движение ползунка
        self.bind("<ButtonPress-1>", self.click_position)  # Обработка клика на дорожке

    def start_drag(self, event):
        """Устанавливает флаг начала перетаскивания"""
        self.dragging = True

    def stop_drag(self, event):
        """Сбрасывает флаг после завершения перетаскивания"""
        self.dragging = False

    def on_drag(self, event):
        """Обрабатывает движение ползунка при его перетаскивании"""
        if self.dragging:
            # Ограничиваем x-координату ползунка в пределах допустимых значений
            x = min(max(event.x, self.padding), self.width - self.padding)
            # Обновляем позицию прогресса и вызываем команду
            self.update_progress_position(x)
            if self.command:
                progress = (x - self.padding) / (self.width - 2 * self.padding) * 100
                self.command(progress)

    def click_position(self, event):
        """Обрабатывает клик на дорожке прогресс-бара"""
        # Ограничиваем x-координату клика в пределах дорожки
        x = min(max(event.x, self.padding), self.width - self.padding)
        # Обновляем позицию прогресса и вызываем команду, если она указана
        self.update_progress_position(x)
        if self.command:
            progress = (x - self.padding) / (self.width - 2 * self.padding) * 100
            self.command(progress)

    def update_progress_position(self, x):
        """
        Обновляет положение активной части прогресс-бара и ползунка.

        Args:
        x: Новая x-координата конца активной части прогресс-бара.
        """
        # Обновляем позицию активной части прогресс-бара
        self.coords(self.fg_bar, self.padding, self.height // 2 - 3, x, self.height // 2 + 3)
        # Обновляем положение ползунка
        self.coords(self.knob, x - self.knob_radius, self.height // 2 - self.knob_radius,
                    x + self.knob_radius, self.height // 2 + self.knob_radius)
        # Обновляем значение прогресса в процентах
        self.progress_value = (x - self.padding) / (self.width - 2 * self.padding) * 100

    def set_progress(self, progress):
        """
        Устанавливает прогресс-бара на указанный процент (от 0 до 100).

        Args:
        progress: Значение прогресса (в процентах).
        """
        # Ограничиваем прогресс в пределах от 0 до 100
        progress = max(0, min(progress, 100))
        # Переводим процент прогресса в x-координату на шкале
        x = self.padding + (progress / 100) * (self.width - 2 * self.padding)
        # Обновляем положение прогресс-бара и ползунка
        self.update_progress_position(x)

    def update_bg_color(self, new_color):
        """Обновляет цвет фона прогресс-бара"""
        self.bg_color = new_color  # Сохраняем новый цвет фона
        self.itemconfig(self.bg_bar, fill=new_color)  # Обновляем фоновый цвет на холсте

    def update_knob_color(self, new_color):
        """Обновляет цвет ползунка"""
        self.knob_color = new_color  # Сохраняем новый цвет ползунка
        self.itemconfig(self.knob, fill=new_color)  # Обновляем цвет ползунка на холсте
