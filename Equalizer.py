import pygame
import threading
import numpy as np
from tkinter import *
from numpy.fft import fft
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AudioVisualizer:
    def __init__(self, root, main_app):
        # Конструктор для инициализации визуализатора, принимает корневое окно (root) и главное приложение (main_app)
        self.root = root  # Ссылка на корневое окно tkinter
        self.main_app = main_app  # Ссылка на главный объект приложения
        self.root.title("Audio Visualization")  # Устанавливаем заголовок окна
        self.root.geometry("300x300")  # Размеры окна визуализатора
        self.root.resizable(False, False)  # Запрещаем изменение размеров окна

        # Параметры для аудио: размер блока CHUNK определяет количество сэмплов за раз, RATE — частота дискретизации
        self.CHUNK = 1024  # Число сэмплов, обрабатываемых за одно обновление
        self.RATE = 44100  # Частота дискретизации (Гц)

        # Переменные для контроля обновлений и настройки темы
        self.update_job = None  # Переменная для хранения задачи обновления интерфейса
        self.is_updating = False  # Флаг, указывающий на выполнение обновления
        self.is_day_theme = None  # Флаг для отслеживания текущей темы
        self.running = True  # Управляющий флаг для остановки визуализации
        self.smoothing_factor = 0.8  # Коэффициент сглаживания амплитуд для визуализации
        self.smoothed_amplitudes = np.zeros(self.CHUNK // 2)  # Массив для сглаженных значений амплитуд
        self.on_close_callback = None  # Коллбэк для уведомления основного класса
        self.audio_samples = None  # Переменная для хранения данных аудио-сэмплов

        pygame.mixer.init()  # Инициализация аудио-микшера с помощью библиотеки pygame

        self.visualization_type = StringVar(value='Bar')  # Тип визуализации (начальное значение — "Bar")

        # Создаем меню выбора типа визуализации, добавляя радиокнопки для каждого типа
        self.menu_bar = Frame(self.root, height=20)  # Верхняя панель для размещения меню
        self.menu_bar.pack(side="top", fill="x")  # Размещение меню вверху окна

        # Настройка графика для визуализации, отключаем оси
        self.fig, self.ax = plt.subplots(figsize=(8, 8))  # Создаем фигуру и ось matplotlib для рисования
        self.ax.axis('off')  # Отключаем отображение осей графика
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)  # Привязка графика к tkinter холсту
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)  # Размещаем холст в окне

        # Кнопка для открытия меню выбора типа визуализации
        self.visualizer_menu_button = Menubutton(self.menu_bar, image=self.main_app.graph_photo, cursor='hand2',
                                                 borderwidth=0)  # Устанавливаем изображение для кнопки
        self.visualizer_menu_button.pack(side="left", padx=5)  # Размещение кнопки в меню с отступом слева

        # Создаем само меню с типами визуализаций и привязываем его к кнопке
        self.visualizer_menu = Menu(self.visualizer_menu_button, tearoff=0, cursor='hand2')
        for vis_type in ['Bar', 'Line', 'Circle']:  # Циклом добавляем каждый тип в меню
            self.visualizer_menu.add_radiobutton(label=vis_type, variable=self.visualization_type, value=vis_type)
        self.visualizer_menu_button.config(menu=self.visualizer_menu)  # Привязываем меню к кнопке

        # Устанавливаем обработчик события для корректного закрытия окна визуализатора
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.start_visualization()  # Старт визуализации

    def load_samples(self, samples):
        """Метод для загрузки аудио-сэмплов, которые будут визуализированы"""
        self.audio_samples = samples  # Сохраняем сэмплы в переменную экземпляра

    def start_visualization(self):
        """Метод для старта процесса визуализации в отдельном потоке"""
        if not self.is_updating:  # Если уже не идет обновление
            self.is_updating = True  # Помечаем, что идет обновление
            thread = threading.Thread(target=self.update_visualization)  # Создаем поток
            thread.start()  # Запускаем поток для обновления

    def update_visualization(self):
        """Обновление визуализации по типу, выбранному пользователем"""
        try:
            # Продолжаем цикл, пока визуализация включена и воспроизведение активно
            while self.running and pygame.mixer.music.get_busy():
                position_ms = pygame.mixer.music.get_pos()  # Текущая позиция в треке в миллисекундах
                position_samples = int(position_ms * self.RATE / 1000)  # Переводим позицию в сэмплы
                samples = self.get_audio_data(self.CHUNK, position_samples)  # Получаем данные аудио

                # Применяем преобразование Фурье для выделения амплитуд
                yf = fft(samples)
                amplitudes = 2.0 / self.CHUNK * np.abs(yf[:self.CHUNK // 2])

                self.smoothing_factor = 0.8  # Коэффициент сглаживания амплитуд для визуализации
                # Сглаживание значений амплитуд с помощью коэффициента
                self.smoothed_amplitudes = (
                        self.smoothing_factor * self.smoothed_amplitudes +
                        (1 - self.smoothing_factor) * amplitudes
                )

                # Очищаем текущий график и добавляем новый, основываясь на типе визуализации
                self.ax.clear()
                self.ax.axis('off')  # Отключаем оси для графика
                vis_type = self.visualization_type.get()  # Получаем текущий выбранный тип визуализации
                if vis_type == 'Bar':
                    self.plot_bar(self.smoothed_amplitudes)
                elif vis_type == 'Line':
                    self.plot_line(self.smoothed_amplitudes)
                elif vis_type == 'Circle':
                    self.plot_circle(self.smoothed_amplitudes)

                self.canvas.draw()  # Обновляем tkinter-холст с новым изображением графика

                self.root.after(25, lambda: None)  # Добавляем небольшую паузу

        finally:
            self.is_updating = False  # Помечаем, что обновление завершено

    def plot_bar(self, amplitudes):
        """Метод для отрисовки гистограммы амплитуд"""
        num_bars = 20  # Количество столбцов в гистограмме
        color = plt.cm.plasma(np.linspace(0, 1, num_bars)) if self.is_day_theme else plt.cm.twilight(
            np.linspace(0, 1, num_bars))
        # Создаем гистограмму с амплитудами и устанавливаем цвет в зависимости от темы
        self.ax.bar(range(num_bars), amplitudes[:num_bars], color=color)
        max_amplitude = np.max(amplitudes)
        if max_amplitude > 0:
            self.ax.set_ylim(0, max_amplitude * 1.5)
        else:
            self.ax.set_ylim(0, 1)

    def plot_line(self, amplitudes):
        """Метод для отрисовки линейного графика амплитуд"""
        num_bars = 100
        color = 'blue' if self.is_day_theme else '#9a8cdb'
        self.ax.plot(amplitudes[:num_bars], color=color, lw=2)  # Линия, представляющая амплитуды
        self.ax.set_ylim(0, np.max(amplitudes) * 1.1)  # Настраиваем масштаб по вертикали
        self.ax.set_xticks([])

    def plot_circle(self, amplitudes):
        """Метод для круговой визуализации амплитуд"""
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-1.5, 1.5)
        num_bars = 65  # Количество "лучей" круга
        angles = np.linspace(0, 2 * np.pi, num_bars, endpoint=False)
        max_amplitude = max(amplitudes[:num_bars]) if max(
            amplitudes[:num_bars]) > 0 else 1  # Максимальная амплитуда для нормировки
        for i in range(num_bars):
            angle = angles[i]
            amplitude = amplitudes[i] / max_amplitude
            x_start = np.cos(angle)
            y_start = np.sin(angle)
            x_end = (1 + amplitude * 0.5) * np.cos(angle)
            y_end = (1 + amplitude * 0.5) * np.sin(angle)
            color = plt.cm.inferno(amplitude) if self.is_day_theme else plt.cm.viridis(amplitude)
            self.ax.plot([x_start, x_end], [y_start, y_end], color=color, lw=5)

    def get_audio_data(self, chunk_size, position):
        """Получение сэмплов для визуализации"""
        # Проверяем, загружены ли аудио-сэмплы. Если нет, возвращаем массив из нулей нужного размера.
        if self.audio_samples is None:
            return np.zeros(chunk_size)  # Возвращаем нулевой массив для избежания ошибок

        # Определяем начальную и конечную позиции для извлечения данных
        start = position  # Начальный индекс для извлечения сэмплов
        end = start + chunk_size  # Конечный индекс (start + количество сэмплов)

        # Извлекаем сэмплы из загруженных аудиоданных
        samples = self.audio_samples[start:end]  # Получаем массив сэмплов от start до end

        # Проверяем, хватает ли сэмплов в указанном диапазоне
        if len(samples) < chunk_size:
            # Если сэмплов не хватает, добавляем нули в конец массива до нужного размера
            samples = np.pad(samples, (0, chunk_size - len(samples)), mode='constant')

        return samples  # Возвращаем массив сэмплов

    def on_close(self):
        """Метод для обработки закрытия окна визуализатора."""
        if self.on_close_callback:
            self.on_close_callback()
        self.running = False  # Устанавливаем флаг, чтобы завершить цикл визуализации
        self.root.withdraw()  # Закрываем окно визуализатора, не уничтожая его

    def update_theme_visualizer(self, is_day_theme):
        """Обновление темы визуализатора в зависимости от основной темы"""
        if not self.root.winfo_exists():
            return  # Прекращаем выполнение, если окно уже закрыто

        self.is_day_theme = is_day_theme
        if self.is_day_theme:
            self.root.config(bg="#f0f0f0")
            self.menu_bar.config(bg='#f0f0f0')
            self.visualizer_menu_button.config(image=self.main_app.graph_photo, bg='#f0f0f0',
                                               activebackground='#f0f0f0')
            self.visualizer_menu.config(bg='#f0f0f0', activebackground='lightgray', activeforeground='black',
                                        foreground='black')
            self.fig.patch.set_facecolor("#f0f0f0")  # Обновляем фон фигуры
        else:
            self.root.config(bg="#302d38")
            self.menu_bar.config(bg="#302d38")
            self.visualizer_menu_button.config(image=self.main_app.graph_photo_night, bg='#302d38',
                                               activebackground='#302d38')
            self.visualizer_menu.config(bg='#302d38', activebackground='#201e26', activeforeground='white',
                                        foreground='white')
            self.fig.patch.set_facecolor("#302d38")  # Обновляем фон фигуры

        self.canvas.draw()  # Перерисовываем холст
