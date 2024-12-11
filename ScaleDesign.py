from tkinter import *


class CustomSlider(Canvas):
    def __init__(self, parent, from_=0, to=100, initial=50, width=150, height=50, slider_color="blue",
                 trough_color="lightgray", command=None):
        """
        Создает пользовательский слайдер

        Параметры:
        - parent: родительский виджет для размещения слайдера.
        - from_: минимальное значение на шкале слайдера.
        - to: максимальное значение на шкале слайдера.
        - initial: начальное значение слайдера.
        - width: ширина слайдера.
        - height: высота слайдера.
        - slider_color: цвет ползунка.
        - trough_color: цвет дорожки.
        - command: функция обратного вызова при изменении значения.
        """

        super().__init__(parent, width=width, height=height, highlightthickness=0)
        self.from_ = from_
        self.to = to
        self.value = initial
        self.slider_color = slider_color
        self.trough_color = trough_color
        self.command = command

        self.width = width
        self.height = height

        # Определяем начальные и конечные точки дорожки с учетом отступов
        self.track_start = 100
        self.track_end = self.width - 100
        # Рисуем дорожку
        self.track = self.create_line(self.track_start, height // 2, self.track_end, height // 2,
                                      fill=self.trough_color, width=12, capstyle=ROUND)

        # Параметры ползунка
        self.slider_radius = 8
        self.slider_x = self.value_to_pos(self.value)
        self.slider = self.create_oval(
            self.slider_x - self.slider_radius, height // 2 - self.slider_radius,
            self.slider_x + self.slider_radius, height // 2 + self.slider_radius,
            fill=self.slider_color, outline=""
        )

        # Привязка событий мыши
        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)

    def value_to_pos(self, value):
        """Преобразует значение слайдера в позицию на Canvas."""
        return self.track_start + (value - self.from_) / (self.to - self.from_) * (self.track_end - self.track_start)

    def pos_to_value(self, pos):
        """Преобразует позицию на Canvas в значение слайдера."""
        pos = min(max(pos, self.track_start), self.track_end)
        return self.from_ + (pos - self.track_start) / (self.track_end - self.track_start) * (self.to - self.from_)

    def click(self, event):
        """Обрабатывает клик на слайдере, перемещая ползунок к позиции клика"""
        self.move_slider(event.x)

    def drag(self, event):
        """Обрабатывает перетаскивание ползунка при удерживании кнопки мыши"""
        self.move_slider(event.x)

    def move_slider(self, x):
        """
        Перемещает ползунок в новую позицию и обновляет значение слайдера

        Args:
        x: новая позиция по оси X, куда следует переместить ползунок.
        """
        # Ограничиваем движение ползунка в пределах дорожки
        x = min(max(x, self.track_start), self.track_end)

        # Обновляем координаты ползунка
        self.coords(
            self.slider,
            x - self.slider_radius, self.height // 2 - self.slider_radius,
            x + self.slider_radius, self.height // 2 + self.slider_radius
        )

        # Обновляем значение слайдера на основе новой позиции ползунка
        self.value = int(self.pos_to_value(x))

        # Вызываем команду обратного вызова, если она передана
        if self.command:
            self.command(self.value)

    def set(self, param):
        pass

    def update_bg_color(self, new_color):
        """Обновляет цвет дорожки слайдера."""
        self.trough_color = new_color
        self.itemconfig(self.track, fill=new_color)

    def update_slider_color(self, new_color):
        """Обновляет цвет ползунка."""
        self.slider_color = new_color
        self.itemconfig(self.slider, fill=new_color)
