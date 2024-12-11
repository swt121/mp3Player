from tkinter import *


class CustomScrollbar(Canvas):
    def __init__(self, parent, text_widget, *args, **kwargs):
        """
        Создает кастомный скроллбар для текстового виджета

        Args:
        parent: родительский виджет, в котором размещается скроллбар;
        text_widget: виджет текста, для которого создается скроллбар;
        args и kwargs: дополнительные аргументы для Canvas.
        """
        # Устанавливаем цвет фона и ползунка, переданный в аргументах, или используем значения по умолчанию.
        self.bg_color = kwargs.pop('bg_color', '#f0f0f0')
        self.slider_color = kwargs.pop('slider_color', '#909090')
        self.slider_hover_color = kwargs.pop('slider_hover_color', '#707070')
        self.width = kwargs.pop('width', 15)  # Ширина скроллбара

        # Инициализация Canvas как основы для скроллбара с указанными параметрами
        super().__init__(parent, *args, bg=self.bg_color, highlightthickness=0, width=self.width)

        # Связь с текстовым виджетом, для которого будет отображаться скроллбар
        self.text_widget = text_widget
        self.slider_height = 50  # Начальная высота ползунка
        self.start_y = None  # Начальная координата для отслеживания позиции ползунка при перетаскивании
        self.slider = self.create_rectangle(0, 0, self.width, self.slider_height, fill=self.slider_color, outline="")

        # Привязка прокрутки с помощью колесика мыши
        self.text_widget.bind("<MouseWheel>", self.on_mouse_wheel)

        # Настройка yscrollcommand для синхронизации скроллбара с текстом
        self.text_widget.config(yscrollcommand=self.update_from_text)

        # Привязка событий: изменение размеров, клик, перетаскивание и смена цвета при наведении курсора
        self.bind("<Configure>", self.update_scrollbar)
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Enter>", lambda _: self.change_slider_color(self.slider_hover_color))
        self.bind("<Leave>", lambda _: self.change_slider_color(self.slider_color))

    def on_mouse_wheel(self, event):
        """Прокручивает текстовый виджет и обновляет положение скроллбара при прокрутке колесом мыши"""
        # Прокручиваем текстовый виджет
        self.text_widget.yview_scroll(-1 * int(event.delta / 120), "units")
        # Обновляем положение скроллбара
        self.update_from_text(self.text_widget.yview()[0], self.text_widget.yview()[1])

    def update_scrollbar(self, event=None):
        """Обновляет размеры и положение ползунка в зависимости от высоты окна"""
        # Высота скроллбара и текстового виджета
        canvas_height = self.winfo_height()
        text_height = max(1, self.text_widget.winfo_height())

        # Вычисляем высоту ползунка как отношение высот канвы и текста
        self.slider_height = min(canvas_height, int((canvas_height / text_height) * canvas_height))

        # Обновляем положение ползунка с новой высотой
        self.coords(self.slider, 0, 0, self.width, self.slider_height)

    def on_click(self, event):
        """Обрабатывает клик на ползунке и сохраняет начальную координату клика"""
        self.start_y = event.y  # Запоминаем начальную позицию клика по оси Y

    def on_drag(self, event):
        """Обрабатывает перетаскивание ползунка и прокручивает текст в соответствии с его положением"""
        if self.start_y is None:  # Проверка, что начальная позиция клика определена
            return
        # Вычисляем смещение ползунка по Y и перемещаем его
        dy = event.y - self.start_y
        self.move(self.slider, 0, dy)
        self.start_y = event.y  # Обновляем начальную позицию

        # Ограничиваем ползунок в пределах канвы и синхронизируем его положение с текстом
        self.limit_slider()
        self.scroll_text()

    def limit_slider(self):
        """Ограничивает перемещение ползунка в пределах высоты канвы"""
        # Получаем текущее положение ползунка
        y1, y2 = self.coords(self.slider)[1], self.coords(self.slider)[3]
        canvas_height = self.winfo_height()

        # Ограничиваем положение верхней границы ползунка, чтобы он не выходил за пределы канвы
        y1 = max(0, min(y1, canvas_height - self.slider_height))

        # Устанавливаем обновленное положение ползунка
        self.coords(self.slider, 0, y1, self.width, y1 + self.slider_height)

    def scroll_text(self):
        """Синхронизирует прокрутку текста с положением ползунка"""
        y1 = self.coords(self.slider)[1]  # Получаем верхнюю границу ползунка
        canvas_height = self.winfo_height() - self.slider_height  # Доступная для перемещения высота

        if canvas_height > 0:  # Проверка, что высота позволяет перемещать ползунок
            # Вычисляем позицию ползунка как долю от высоты канвы
            slider_pos = y1 / canvas_height
            self.text_widget.yview_moveto(slider_pos)  # Прокручиваем текстовый виджет

    def update_from_text(self, first, _):
        """Обновляет позицию ползунка в соответствии с прокруткой текста"""
        first = float(first)  # Преобразуем начальную позицию в float для дальнейших вычислений
        self.update_slider_position(first)  # Устанавливаем положение ползунка

    def update_slider_position(self, first):
        """Устанавливает позицию ползунка на основе прокрутки текстового виджета"""
        canvas_height = self.winfo_height()  # Высота канвы
        new_y1 = first * canvas_height  # Вычисляем новое положение верхней границы ползунка
        # Устанавливаем новые координаты ползунка
        self.coords(self.slider, 0, new_y1, self.width, new_y1 + self.slider_height)

    def change_slider_color(self, color):
        """Меняет цвет ползунка (например, при наведении курсора)"""
        self.itemconfig(self.slider, fill=color)  # Устанавливаем цвет для ползунка

    def set_slider_color(self, color, hover_color=None):
        """Устанавливает цвета ползунка и его состояния при наведении"""
        self.slider_color = color  # Основной цвет ползунка
        self.slider_hover_color = hover_color or self.slider_hover_color  # Цвет при наведении (по умолчанию)
        self.itemconfig(self.slider, fill=self.slider_color)  # Применяем основной цвет ползунка

    def set_bg_color(self, color):
        """Устанавливает цвет фона скроллбара."""
        self.bg_color = color  # Сохраняем цвет фона
        self.config(bg=self.bg_color)  # Применяем цвет фона к канве
