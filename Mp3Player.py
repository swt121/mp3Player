import os
import time
import pygame
import shutil
import requests
import tempfile
import numpy as np
from tkinter import *
from PIL import Image, ImageTk
from pydub import AudioSegment
from Search import SearchWindow
from ScaleDesign import CustomSlider
from Equalizer import AudioVisualizer
from tkinter import messagebox, filedialog
from ScrollBarDesign import CustomScrollbar
from ProgressBarDesign import CustomProgressBar



class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title('MP3 Player')
        self.root.geometry('400x600')

        pygame.mixer.init()  # Инициализация pygame для воспроизведения аудио

        self.JAMENDO_CLIENT_ID = 'caafd71c'  # Jamendo API Client ID
        self.is_playing = False  # Флаг для проигрывания
        self.is_playing_temp = False  # Флаг для временного проигрывания
        self.random_mode = False  # Флаг для случайного режима
        self.is_day_theme = True  # Начальный режим (дневной)
        self.track_length = 0  # Длина трека
        self.start_time = 0  # Время начала воспроизведения
        self.paused_time = 0  # Время, на котором трек был приостановлен
        self.current_track_index = 0  # Индекс текущего трека
        self.audio_visualizer = None  # Ссылка на визуализатор
        self.search_window = None  # Ссылка на окно поиска
        self.played_tracks = []

        # Получаем список треков из папки
        self.music_folder = 'music'  # Папка с музыкой
        self.track_list = [file for file in os.listdir(self.music_folder) if file.endswith('.mp3')]  # Список треков
        self.temp_dir = tempfile.mkdtemp()  # Временная папка для временных треков

        # Плейлист будет содержать как локальные, так и онлайн-треки
        self.playlist = self.track_list.copy()  # Начальный плейлист с локальными треками

        # Используем эту фотографию для типов визуализации в окне аудио визуализации
        self.graph_photo = ImageTk.PhotoImage(
            Image.open("pics//graph.png").resize((25, 25)))
        self.graph_photo_night = ImageTk.PhotoImage(
            Image.open("pics//graph_night.png").resize((25, 25)))

        # Создаем свою панель
        self.menu_bar = Frame(self.root, bg="#f0f0f0", height=20)

        # Создаем кнопку для выбора тем
        self.photo_theme = ImageTk.PhotoImage(
            Image.open("C://Users//legor//PycharmProjects//mp3Player//pics//sun.png").resize((30, 30)))
        self.photo_theme_night = ImageTk.PhotoImage(
            Image.open("C://Users//legor//PycharmProjects//mp3Player//pics//moon.png").resize((25, 25)))

        self.theme_menu_button = Menubutton(self.menu_bar, image=self.photo_theme,
                                            cursor='hand2', borderwidth=0)
        self.theme_menu_button.pack(side="left", padx=5)

        # Создаем выпадающее меню для выбора тем
        self.theme_menu = Menu(self.theme_menu_button, tearoff=0, activebackground='gray',
                               activeforeground='black', cursor='hand2', bg='#f0f0f0')
        self.theme_menu.add_command(label="Day Mode", command=self.set_day_mode)
        self.theme_menu.add_command(label="Night Mode", command=self.set_night_mode)
        self.theme_menu_button.config(menu=self.theme_menu)

        # Создаем кнопку для меню "AudioVisualizer"
        self.photo_audio = ImageTk.PhotoImage(
            Image.open("pics//audio.png").resize((25, 25)))
        self.photo_audio_night = ImageTk.PhotoImage(
            Image.open("pics//audio_night.png").resize((30, 30)))
        self.visualizer_button = Button(self.menu_bar, image=self.photo_audio,
                                        cursor='hand2', borderwidth=0, command=self.open_visualizer)
        self.visualizer_button.pack(side="left", padx=5)

        # Создаем кнопку "Search"
        self.photo_search = ImageTk.PhotoImage(
            Image.open("pics//search.png").resize((20, 20)))
        self.photo_search_night = ImageTk.PhotoImage(
            Image.open("pics//search_night.png").resize((20, 20)))
        self.search_button = Button(self.menu_bar, image=self.photo_search,
                                    cursor='hand2', borderwidth=0, command=self.open_search_window)
        self.search_button.pack(side="left", padx=5)

        # Кнопка "Shuffle"
        self.shuffle_photo = ImageTk.PhotoImage(
            Image.open("pics//shuffle.png").resize((25, 25)))
        self.shuffle_photo_night = ImageTk.PhotoImage(
            Image.open("pics//shuffle_night.png").resize((25, 25)))

        self.shuffle_button = Button(self.menu_bar, image=self.shuffle_photo, borderwidth=0,
                                     command=self.toggle_shuffle, cursor='hand2')
        self.shuffle_button.pack(side="left", padx=5)

        # Кнопка "Удалить"
        self.delete_photo = ImageTk.PhotoImage(
            Image.open("pics//delete.png").resize((25, 25)))
        self.delete_photo_night = ImageTk.PhotoImage(
            Image.open("pics//delete_night.png").resize((30, 30)))

        self.delete_button = Button(self.menu_bar, cursor='hand2', borderwidth=0, image=self.delete_photo,
                                    command=self.delete_track)
        self.delete_button.pack(side="right", padx=5)

        # Кнопка для добавления своего трека
        self.photo_add = ImageTk.PhotoImage(
            Image.open("pics//add.png").resize((27, 27)))
        self.photo_add_night = ImageTk.PhotoImage(
            Image.open("pics//add_night.png").resize((30, 30)))

        self.move_button = Button(self.menu_bar, cursor='hand2', borderwidth=0, image=self.photo_add,
                                  command=self.mp3_to_folder)
        self.move_button.pack(side='right', padx=5)

        # Упаковываем кастомную верхнюю панель
        self.menu_bar.pack(fill="x")

        # Интерфейс
        self.track_label = Label(self.root, text="No track playing", font=("Helvetica", 12))
        self.track_label.pack(pady=20)

        # Кнопки управления
        self.control_frame = Frame(self.root)
        self.control_frame.pack(pady=20)

        # Кнопка проигрывания/паузы трека
        self.photo_play = ImageTk.PhotoImage(
            Image.open("pics//play.png").resize((35, 35)))
        self.photo_pause = ImageTk.PhotoImage(
            Image.open("pics//pause.png").resize((35, 35)))

        self.photo_pause_night = ImageTk.PhotoImage(
            Image.open("pics//pause_night.png").resize((35, 35)))
        self.photo_play_night = ImageTk.PhotoImage(
            Image.open("pics//play_night.png").resize((35, 35)))

        self.play_button = Button(self.control_frame, borderwidth=0, image=self.photo_play,
                                  command=self.play_pause, cursor='hand2')
        self.play_button.grid(row=0, column=1, padx=10)

        # Кнопка предыдущего трека
        self.photo_prev = ImageTk.PhotoImage(
            Image.open("pics//prev.png").resize((25, 25)))
        self.photo_prev_night = ImageTk.PhotoImage(
            Image.open("pics//prev_night.png").resize((25, 25)))

        self.prev_button = Button(self.control_frame, image=self.photo_prev, command=self.prev_track,
                                  cursor='hand2', borderwidth=0)
        self.prev_button.grid(row=0, column=0, padx=10)

        # Кнопка следующего трека
        self.photo_next = ImageTk.PhotoImage(
            Image.open("pics//next.png").resize((25, 25)))
        self.photo_next_night = ImageTk.PhotoImage(
            Image.open("pics//next_night.png").resize((25, 25)))

        self.next_button = Button(self.control_frame, image=self.photo_next, command=self.next_track, cursor='hand2',
                                  borderwidth=0)
        self.next_button.grid(row=0, column=2, padx=10)

        # Фрейм для треков и скроллбара
        self.list_frame = Frame(self.root)
        self.list_frame.pack(fill=BOTH, expand=True)

        self.track_listbox = Listbox(self.list_frame, selectmode=SINGLE, activestyle='none',
                                     yscrollcommand=lambda f, l: self.scroll_bar.set(f, l))

        # Добавление треков из списка в Listbox
        for track in self.track_list:
            track_display_name = track.replace('.mp3', '')  # Удаляем расширение .mp3
            self.track_listbox.insert(END, track_display_name)

        self.track_listbox.pack(side=LEFT, fill=BOTH, expand=True)

        # Инициализация скроллбара
        self.scrollbar = CustomScrollbar(self.list_frame, self.track_listbox, bg_color="#f0f0f0",
                                         slider_color="#909090", slider_hover_color="#707070", width=15)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Инициализация ползунка громкости
        self.volume_scale = CustomSlider(self.root, from_=0, to=100, initial=50, width=300, height=50,
                                         slider_color='gray', trough_color='lightgray', command=self.set_volume)
        self.volume_scale.pack()

        # Фрейм для прогресса трека
        self.progress_frame = Frame(self.root)
        self.progress_frame.pack(pady=10)

        # Инициализация начального времени трека
        self.start_time_label = Label(self.progress_frame, text='00:00', font=('Helvetica', 10))
        self.start_time_label.pack(side=LEFT, padx=5)

        # Инициализация прогрессбара
        self.progress_bar = CustomProgressBar(self.progress_frame, width=300, height=10, bg_color='lightgray',
                                              fg_color='#1DB954', knob_color='#696969', command=self.seek_track)
        self.progress_bar.pack(side=LEFT, padx=5)

        # Инициализация конечного времени трека
        self.end_time_label = Label(self.progress_frame, text='00:00', font=('Helvetica', 10))
        self.end_time_label.pack(side=LEFT, padx=5)

        # Привязка клавиш для управления
        self.track_listbox.bind('<Up>', self.on_arrow_up)
        self.track_listbox.bind('<Down>', self.on_arrow_down)
        self.track_listbox.bind('<Return>', self.on_enter)
        self.track_listbox.bind('<space>', self.on_space)

        self.track_listbox.selection_set(0)  # Устанавливаем первый трек как выбранный по умолчанию
        self.track_listbox.focus_set()  # Устанавливаем фокус на Listbox

        self.update_progress()  # Обновление прогресса для Progress Bar
        self.set_day_mode()  # Устанавливаем начальную тему

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Протокол для закрытия окна плеера

    def load_track(self, index):
        """Загрузка трека и обновление метки."""
        # Получаем путь к файлу трека на основе индекса и папки с музыкой
        track_path = os.path.join(self.music_folder, self.track_list[index])

        # Загружаем аудиофайл и конвертируем его в моно (1 канал), затем получаем массив с аудио данными
        audio_segment = AudioSegment.from_mp3(track_path).set_channels(1)
        self.audio_samples = np.array(audio_segment.get_array_of_samples())

        # Если существует визуализатор аудио, передаем ему аудио данные для дальнейшей визуализации
        if self.audio_visualizer:
            self.audio_visualizer.load_samples(self.audio_samples)

        # Загружаем трек в Pygame для воспроизведения
        pygame.mixer.music.load(os.path.join(self.music_folder, self.track_list[index]))

        # Обновляем метку, показывающую текущий трек (отображаем название без расширения .mp3)
        self.track_label.config(text=f"Playing: {self.track_list[index].replace('.mp3', '')}")

        # Получаем продолжительность трека и обновляем метку времени конца трека
        self.track_length = pygame.mixer.Sound(track_path).get_length()
        self.end_time_label.config(text=self.format_time(self.track_length))

        # Обнуляем прогресс-бар и устанавливаем начальное время трека
        self.progress_bar.set_progress(0)
        self.start_time_label.config(text='00:00')

    def play_pause(self):
        """Воспроизведение или пауза трека"""
        # Получаем индекс выбранного трека в списке
        selected_index = self.track_listbox.curselection()
        if not self.is_playing:
            # Если трек не воспроизводится, начинаем воспроизведение
            if not pygame.mixer.music.get_busy():
                # В режиме случайного воспроизведения выбираем случайный трек
                if self.random_mode and self.is_playing:
                    self.current_track_index = np.random.randint(0, len(self.playlist))
                else:
                    # В противном случае используем выбранный трек
                    self.current_track_index = selected_index[0]

                # Загружаем и начинаем воспроизведение трека с позиции паузы (если таковая была)
                self.load_track(self.current_track_index)
                pygame.mixer.music.play(start=self.paused_time)  # Воспроизведение с позиции паузы
                self.start_time = time.time() - self.paused_time  # Обновляем время для корректного отсчета
            else:
                # Если музыка уже воспроизводится, просто возобновляем воспроизведение
                pygame.mixer.music.unpause()
                pygame.mixer.music.set_pos(self.paused_time)  # Установка позиции на сохраненное время
                self.start_time = time.time() - self.paused_time  # Обновляем время, когда трек возобновляется

            # Меняем состояние воспроизведения
            self.is_playing = True

            # Меняем изображение на кнопке play/pause в зависимости от темы
            if self.is_day_theme:
                self.play_button.config(image=self.photo_pause)
            else:
                self.play_button.config(image=self.photo_pause_night)

            # Запускаем визуализацию, если окно уже открыто
            if self.audio_visualizer:
                self.audio_visualizer.start_visualization()
        else:
            # Если музыка воспроизводится, ставим ее на паузу
            pygame.mixer.music.pause()
            self.is_playing = False

            # Сохраняем время, на котором трек был приостановлен
            self.paused_time = time.time() - self.start_time

            # Обновляем изображение на кнопке play/pause в зависимости от темы
            if self.is_day_theme:
                self.play_button.config(image=self.photo_play)
            else:
                self.play_button.config(image=self.photo_play_night)

        # Обновляем выделение в списке треков
        self.update_listbox_selection()

    def next_track(self):
        """Переключение на следующий трек"""
        # В режиме случайного воспроизведения выбираем случайный трек
        if self.random_mode:
            # В режиме случайного воспроизведения, избегаем повторения треков
            remaining_tracks = [track for track in self.playlist if track not in self.played_tracks]

            if not remaining_tracks:
                # Если все треки уже проиграны, сбрасываем список и перемешиваем
                self.played_tracks = []
                np.random.shuffle(self.playlist)
                remaining_tracks = self.playlist.copy()

            # Выбираем случайный трек из оставшихся
            next_track = np.random.choice(remaining_tracks)
            self.played_tracks.append(next_track)  # Добавляем трек в список проигранных
            self.current_track_index = self.playlist.index(next_track)
        else:
            # По умолчанию выбираем следующий трек
            self.current_track_index = (self.current_track_index + 1) % len(self.track_list)

        # Загружаем новый трек и сбрасываем время воспроизведения
        self.load_track(self.current_track_index)
        self.start_time = 0
        self.paused_time = 0

        # Если музыка не воспроизводится, начинаем воспроизведение
        if not pygame.mixer.music.get_busy():
            self.load_track(self.current_track_index)
            pygame.mixer.music.play(start=self.paused_time)  # Воспроизведение с позиции паузы
            self.start_time = time.time() - self.paused_time  # Обновляем время для корректного отсчета
        else:
            # Если музыка уже воспроизводится, просто возобновляем воспроизведение
            pygame.mixer.music.unpause()
            pygame.mixer.music.set_pos(self.paused_time)  # Установка позиции на сохраненное время
            self.start_time = time.time() - self.paused_time  # Обновляем время, когда трек возобновляется

        # Меняем изображение на кнопке play/pause в зависимости от темы
        if self.is_day_theme:
            self.play_button.config(image=self.photo_pause)
        else:
            self.play_button.config(image=self.photo_pause_night)

        # Обновляем состояние воспроизведения и выделение трека в списке
        self.is_playing = True
        self.update_listbox_selection()
        self.update_visualizations()
        self.update_progress()

    def prev_track(self):
        """Переключение на предыдущий трек"""
        # Переключаемся на предыдущий трек
        self.current_track_index = (self.current_track_index - 1) % len(self.track_list)

        # Загружаем новый трек и сбрасываем время воспроизведения
        self.load_track(self.current_track_index)
        self.start_time = 0
        self.paused_time = 0

        # Если музыка не воспроизводится, начинаем воспроизведение
        if not pygame.mixer.music.get_busy():
            self.load_track(self.current_track_index)
            pygame.mixer.music.play(start=self.paused_time)  # Воспроизведение с позиции паузы
            self.start_time = time.time() - self.paused_time  # Обновляем время для корректного отсчета
        else:
            # Если музыка уже воспроизводится, просто возобновляем воспроизведение
            pygame.mixer.music.unpause()
            pygame.mixer.music.set_pos(self.paused_time)  # Установка позиции на сохраненное время
            self.start_time = time.time() - self.paused_time  # Обновляем время, когда трек возобновляется

        # Меняем изображение на кнопке play/pause в зависимости от темы
        if self.is_day_theme:
            self.play_button.config(image=self.photo_pause)
        else:
            self.play_button.config(image=self.photo_pause_night)

        # Обновляем состояние воспроизведения и выделение трека в списке
        self.is_playing = True
        self.update_listbox_selection()
        self.update_visualizations()

    def toggle_shuffle(self):
        """Переключение режима случайного воспроизведения"""
        self.random_mode = not self.random_mode  # Переключаем значение режима случайного воспроизведения

        if self.random_mode:
            # Включаем случайный режим, перемешиваем плейлист и сбрасываем список проигранных треков
            self.played_tracks = []
            np.random.shuffle(self.playlist)

            # Меняем фон кнопки на светлый цвет, если используется дневная тема
            if self.is_day_theme:
                self.shuffle_button.config(background='lightgray')
            else:
                # Меняем фон кнопки на темный цвет для ночной темы
                self.shuffle_button.config(background='#201e26')
        else:
            # Если режим случайного воспроизведения выключен, восстанавливаем оригинальный порядок треков
            self.playlist = self.track_list.copy()
            self.played_tracks = []  # Сбрасываем список проигранных треков

            # Меняем фон кнопки на стандартный, если дневная тема
            if self.is_day_theme:
                self.shuffle_button.config(background='#f0f0f0')
            else:
                # Меняем фон кнопки на темный цвет для ночной темы
                self.shuffle_button.config(background='#302d38')

    def on_arrow_up(self, event):
        """Навигация по трекам стрелкой вверх"""
        # Проверяем, что текущий индекс не равен нулю, иначе переходим в конец списка
        if self.current_track_index > 0:
            # Если текущий трек не первый, уменьшаем индекс на 1
            self.current_track_index -= 1
        else:
            # Если первый трек, устанавливаем индекс на последний трек
            self.current_track_index = len(self.track_list) - 1

        # Обновляем выделение в списке треков
        self.update_listbox_selection()

    def on_arrow_down(self, event):
        """Навигация по трекам стрелкой вниз"""
        # Проверяем, что текущий индекс не равен последнему треку
        if self.current_track_index < len(self.track_list) - 1:
            # Если текущий трек не последний, увеличиваем индекс на 1
            self.current_track_index += 1
        else:
            # Если последний трек, устанавливаем индекс на первый трек
            self.current_track_index = 0

        # Обновляем выделение в списке треков
        self.update_listbox_selection()

    def on_enter(self, event):
        """Воспроизведение выделенного трека по нажатию Enter"""
        # Получаем индекс выделенного трека из списка
        selected_index = self.track_listbox.curselection()
        if selected_index:
            # Определяем индекс трека
            if self.random_mode and self.is_playing:
                # Если активирован режим случайного воспроизведения и трек уже играет, выбираем случайный трек
                self.current_track_index = np.random.randint(0, len(self.playlist))
            else:
                # Если не в случайном режиме, используем выбранный трек
                self.current_track_index = selected_index[0]

            # Загружаем трек по выбранному индексу
            self.load_track(self.current_track_index)

            # Сбрасываем время воспроизведения и паузы
            self.start_time = 0
            self.paused_time = 0

            # Проверяем, не воспроизводится ли музыка
            if not pygame.mixer.music.get_busy():
                # Если музыка не играет, загружаем и начинаем воспроизведение с позиции паузы
                self.load_track(self.current_track_index)
                pygame.mixer.music.play(start=self.paused_time)  # Воспроизведение с позиции паузы

                # Обновляем стартовое время для отсчета времени воспроизведения
                self.start_time = time.time() - self.paused_time  # Обновляем время для корректного отсчета
            else:
                # Если музыка уже играет, возобновляем воспроизведение с позиции паузы
                pygame.mixer.music.unpause()
                pygame.mixer.music.set_pos(self.paused_time)  # Установка позиции на сохраненное время

                # Обновляем время начала воспроизведения при возобновлении
                self.start_time = time.time() - self.paused_time  # Обновляем время, когда трек возобновляется

            self.is_playing = True  # Устанавливаем флаг, что музыка играет

            # Запускаем визуализацию, если окно уже открыто
            if self.audio_visualizer:
                self.audio_visualizer.start_visualization()

            # Обновляем выделение в списке
            self.update_listbox_selection()

            # Изменяем кнопку на изображение pause в зависимости от темы
            if self.is_day_theme:
                self.play_button.config(image=self.photo_pause)
            else:
                self.play_button.config(image=self.photo_pause_night)

    def on_space(self, event):
        """Воспроизведение или пауза трека"""
        # Проверяем, играет ли музыка
        if not self.is_playing:
            # Если музыка не играет
            if not pygame.mixer.music.get_busy():
                # Если музыка не запущена, загружаем текущий трек по индексу
                self.load_track(self.current_track_index)

                # Начинаем воспроизведение с позиции, где музыка была приостановлена
                pygame.mixer.music.play(start=self.paused_time)  # Воспроизведение с позиции паузы

                # Обновляем стартовое время, чтобы отсчитывать время воспроизведения
                self.start_time = time.time() - self.paused_time  # Обновляем время для корректного отсчета
            else:
                # Если музыка играет, возобновляем воспроизведение
                pygame.mixer.music.unpause()

                # Устанавливаем позицию воспроизведения на то время, на котором трек был приостановлен
                pygame.mixer.music.set_pos(self.paused_time)  # Установка позиции на сохраненное время

                # Обновляем время для отсчета оставшегося времени
                self.start_time = time.time() - self.paused_time  # Обновляем время, когда трек возобновляется

            # Устанавливаем флаг, что музыка теперь воспроизводится
            self.is_playing = True

            # Обновляем изображение кнопки в зависимости от текущей темы (дневной или ночной)
            if self.is_day_theme:
                self.play_button.config(image=self.photo_pause)
            else:
                self.play_button.config(image=self.photo_pause_night)

            # Обновляем визуализацию, если она активирована
            self.update_visualizations()
        else:
            pygame.mixer.music.pause()  # Если музыка уже играет, ставим её на паузу
            self.is_playing = False  # Обновляем флаг, что музыка приостановлена
            self.paused_time = time.time() - self.start_time  # Сохраняем время, на котором трек был приостановлен

            # Обновляем изображение кнопки на play в зависимости от темы
            if self.is_day_theme:
                self.play_button.config(image=self.photo_play)
            else:
                self.play_button.config(image=self.photo_play_night)

    def update_listbox_selection(self):
        """Обновление выделения в списке треков"""
        self.track_listbox.selection_clear(0, END)  # Снять выделение со всех треков
        self.track_listbox.selection_set(self.current_track_index)  # Установить выделение на текущем треке
        self.track_listbox.activate(self.current_track_index)  # Сделать текущий трек активным

    def set_volume(self, volume):
        """Установка громкости"""
        # Устанавливаем громкость трека (pygame работает со значениями от 0 до 1)
        pygame.mixer.music.set_volume(float(volume) / 100)

    def update_progress(self):
        """Обновление прогресса воспроизведения трека на прогресс-баре"""
        # Проверяем, что музыка воспроизводится, и что длительность трека больше 0
        if self.is_playing and self.track_length > 0:
            # Рассчитываем прошедшее время с момента начала воспроизведения
            elapsed_time = time.time() - self.start_time

            # Если трек завершен, переходим к следующему
            if elapsed_time >= self.track_length:
                self.next_track()
                return

            # Рассчитываем прогресс в процентах
            progress = (elapsed_time / self.track_length) * 100
            # Обновляем значение прогресс-бара
            self.progress_bar.set_progress(progress)

            # Обновляем отображение времени, прошедшего с начала воспроизведения
            self.start_time_label.config(text=self.format_time(elapsed_time))

        # Планируем обновление прогресса через 50 миллисекунд
        self.update_progress_job = self.root.after(50, self.update_progress)

    def seek_track(self, progress_value):
        """Перемотка трека на основе изменения позиции ползунка"""
        # Проверяем, что длительность трека больше 0
        if self.track_length > 0:
            # Вычисляем новое время воспроизведения, исходя из значения ползунка (в процентах)
            new_time = (progress_value / 100) * self.track_length

            # Останавливаем текущую музыку
            pygame.mixer.music.stop()
            # Воспроизводим музыку с новой позиции
            pygame.mixer.music.play(start=new_time)

            # Обновляем стартовое время для отсчета воспроизведения
            self.start_time = time.time() - new_time

            self.is_playing = True  # Устанавливаем флаг, что музыка воспроизводится

    def format_time(self, seconds):
        """Форматирование времени в MM:SS"""
        # Рассчитываем количество минут и секунд
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"

    def set_day_mode(self):
        """Установка дневного режима"""
        self.root.config(bg="#f0f0f0")
        self.track_label.config(bg="#f0f0f0", fg="black")
        self.start_time_label.config(bg="#f0f0f0", fg="black")
        self.end_time_label.config(bg="#f0f0f0", fg="black")
        self.track_listbox.config(bg="#f0f0f0", fg="black", selectbackground="lightgray",
                                  selectforeground='black')
        self.next_button.config(bg='#f0f0f0', image=self.photo_next, activebackground='#f0f0f0')
        self.play_button.config(bg='#f0f0f0', image=self.photo_play, activebackground='#f0f0f0')
        self.prev_button.config(bg='#f0f0f0', image=self.photo_prev, activebackground='#f0f0f0')
        self.progress_frame.config(bg='#f0f0f0')
        self.volume_scale.config(bg='#f0f0f0')
        self.control_frame.config(bg='#f0f0f0')
        self.list_frame.config(bg='#f0f0f0')
        self.progress_bar.update_bg_color("lightgray")
        self.progress_bar.config(bg='#f0f0f0')
        self.progress_bar.update_knob_color('gray')
        self.volume_scale.update_bg_color('lightgray')
        self.volume_scale.update_slider_color('gray')
        self.menu_bar.config(bg='#f0f0f0')
        self.theme_menu_button.config(bg='#f0f0f0', activebackground='#f0f0f0', image=self.photo_theme)
        self.visualizer_button.config(bg='#f0f0f0', activebackground='#f0f0f0', image=self.photo_audio)
        self.theme_menu.config(activebackground='lightgray', fg='black', bg='#f0f0f0',
                               activeforeground='black')
        self.scrollbar.set_bg_color('#f0f0f0')
        self.scrollbar.set_slider_color('#909090', hover_color='#707070')
        self.search_button.config(bg='#f0f0f0', activebackground='#f0f0f0', image=self.photo_search)
        self.delete_button.config(bg='#f0f0f0', activebackground='#f0f0f0', image=self.delete_photo)
        self.move_button.config(bg='#f0f0f0', activebackground='#f0f0f0', image=self.photo_add)

        if self.random_mode:
            self.shuffle_button.config(activebackground='#f0f0f0', background='lightgray',
                                       image=self.shuffle_photo)
        else:
            self.shuffle_button.config(activebackground='#f0f0f0', background='#f0f0f0',
                                       image=self.shuffle_photo)

        if self.is_playing:
            self.play_button.config(image=self.photo_pause)
        else:
            self.play_button.config(image=self.photo_play)

        # Проверяем, существует ли окно поиска
        if hasattr(self, 'search_window') and self.search_window is not None:
            if self.search_window.search_window.winfo_exists():
                self.search_window.update_theme()

        # Обновление темы для визуализатора
        if self.audio_visualizer:
            self.audio_visualizer.update_theme_visualizer(True)

        self.is_day_theme = True

    def set_night_mode(self):
        """Установка ночного режима"""
        self.root.config(bg="#302d38")
        self.track_label.config(bg="#302d38", fg="white")
        self.start_time_label.config(bg="#302d38", fg="white")
        self.end_time_label.config(bg="#302d38", fg="white")
        self.track_listbox.config(bg="#302d38", fg="white", selectbackground="#201e26",
                                  selectforeground="white")
        self.next_button.config(bg='#302d38', activebackground='#302d38', image=self.photo_next_night)
        self.play_button.config(bg='#302d38', activebackground='#302d38', image=self.photo_play_night)
        self.prev_button.config(bg='#302d38', activebackground='#302d38', image=self.photo_prev_night)
        self.volume_scale.config(bg='#302d38')
        self.volume_scale.update_bg_color('#201e26')
        self.volume_scale.update_slider_color('#4657eb')
        self.progress_bar.config(bg='#302d38')
        self.progress_bar.update_bg_color('#201e26')
        self.progress_bar.update_knob_color('#4657eb')
        self.progress_frame.config(bg='#302d38')
        self.control_frame.config(bg='#302d38')
        self.list_frame.config(bg='#302d38')
        self.menu_bar.config(bg='#302d38')
        self.theme_menu_button.config(bg='#302d38', activebackground='#302d38', image=self.photo_theme_night)
        self.visualizer_button.config(bg='#302d38', activebackground='#302d38', image=self.photo_audio_night)
        self.theme_menu.config(activebackground='#201e26', fg='white', bg='#302d38',
                               activeforeground='white')
        self.search_button.config(bg='#302d38', activebackground='#302d38', image=self.photo_search_night)
        self.delete_button.config(bg='#302d38', activebackground='#302d38', image=self.delete_photo_night)
        self.move_button.config(bg='#302d38', activebackground='#302d38', image=self.photo_add_night)
        self.scrollbar.set_bg_color('#302d38')
        self.scrollbar.set_slider_color('#201e26', hover_color='#1f2129')

        if self.random_mode:
            self.shuffle_button.config(activebackground='#302d38', background='#201e26',
                                       image=self.shuffle_photo_night)
        else:
            self.shuffle_button.config(activebackground='#302d38', background='#302d38',
                                       image=self.shuffle_photo_night)

        if self.is_playing:
            self.play_button.config(image=self.photo_pause_night)
        else:
            self.play_button.config(image=self.photo_play_night)

        # Проверяем, существует ли окно поиска
        if hasattr(self, 'search_window') and self.search_window is not None:
            if self.search_window.search_window.winfo_exists():
                self.search_window.update_theme()

        # Обновление темы для визуализатора
        if self.audio_visualizer:
            self.audio_visualizer.update_theme_visualizer(False)

        self.is_day_theme = False

    def open_visualizer(self):
        """Открыть окно визуализатора и применить тему"""
        # Проверяем, существует ли уже атрибут визуализатора или был ли он закрыт
        if not hasattr(self, 'audio_visualizer') or self.audio_visualizer is None:
            # Создаем новый объект визуализатора в новом верхнем окне (Toplevel) от основного окна
            self.audio_visualizer = AudioVisualizer(Toplevel(self.root), self)
            # Применение текущей темы к визуализатору
            self.audio_visualizer.update_theme_visualizer(self.is_day_theme)

            # Передаем ссылку на метод сброса в визуализатор
            self.audio_visualizer.on_close_callback = self.on_visualizer_close

            # Проверяем, воспроизводится ли музыка в данный момент
            if pygame.mixer.music.get_busy():
                # Если музыка воспроизводится, загружаем сэмплы (данные) для визуализатора
                self.audio_visualizer.load_samples(self.audio_samples)
                # Начинаем визуализацию звука
                self.audio_visualizer.start_visualization()

    def on_visualizer_close(self):
        """Сбросить ссылку на визуализатор при его закрытии"""
        self.audio_visualizer = None

    def update_visualizations(self):
        """Обновление визуализаций в реальном времени"""
        # Если визуализатор существует и музыка в данный момент воспроизводится
        if self.audio_visualizer and pygame.mixer.music.get_busy():
            # Запускаем визуализацию звука (обновляем отображение)
            self.audio_visualizer.start_visualization()

        # Устанавливаем повторный вызов этой функции через 55 миллисекунд для постоянного обновления
        self.update_visualization_job = self.root.after(55, self.update_visualizations)

    def delete_track(self):
        """Удаление выбранного трека из плейлиста и папки"""
        # Получаем индекс выбранного трека в списке
        selected_index = self.track_listbox.curselection()

        # Если ничего не выбрано, выводим предупреждение
        if not selected_index:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите трек для удаления.")
            return

        # Получаем название трека из списка и формируем путь к его файлу
        track_name = self.track_listbox.get(selected_index)
        track_filename = track_name + '.mp3'  # Формируем полное имя файла с расширением
        track_path = os.path.join(self.music_folder, track_filename)  # Формируем полный путь к файлу

        # Подтверждаем удаление
        confirm = messagebox.askyesno("Подтверждение удаления", f"Удалить трек '{track_name}' навсегда?")

        # Если пользователь отменил удаление, выходим из функции
        if not confirm:
            return

        try:
            # Удаляем файл из папки
            os.remove(track_path)
            # Удаляем трек из плейлиста и интерфейса
            self.playlist.remove(track_filename)  # Удаляем из списка треков
            self.track_listbox.delete(selected_index)  # Удаляем из списка на экране
            # Информируем пользователя об успешном удалении
            messagebox.showinfo("Удалено", f"Трек '{track_name}' удален из плейлиста и папки.")
        except FileNotFoundError:
            # Если файл не найден, выводим ошибку
            messagebox.showerror("Ошибка", f"Файл '{track_filename}' не найден.")
        except Exception as e:
            # Ловим все остальные ошибки и выводим их
            messagebox.showerror("Ошибка", f"Не удалось удалить трек: {e}")

    def open_search_window(self):
        """Открытие окна поиска"""
        # Проверяем, существует ли окно поиска и активно ли оно
        if not self.search_window or not self.search_window.search_window.winfo_exists():
            # Если окно поиска не существует или было закрыто, создаем новое окно поиска
            self.search_window = SearchWindow(self.root, self)  # Передаем ссылку на себя для взаимодействия
        else:
            self.search_window.search_window.lift()  # Поднимаем окно поиска, если оно уже открыто

    def add_track_to_playlist(self, track_name, track_url):
        """Добавление выбранного трека в плейлист"""
        # Проверяем, является ли URL трека ссылкой на удалённый ресурс (например, http(s) URL)
        if track_url.startswith('http'):
            # Формируем имя файла, заменяя неподходящие символы на нижнее подчеркивание
            sanitized_track_name = "".join([c if c.isalnum() or c in (' ', '_') else "_" for c in track_name])
            filename = f"{sanitized_track_name}.mp3"  # Добавляем расширение .mp3
            file_path = os.path.join(self.music_folder, filename)  # Определяем полный путь к файлу

            # Проверяем, существует ли файл с таким именем в папке music
            if os.path.exists(file_path):
                # Если файл уже существует, показываем пользователю уведомление
                messagebox.showinfo("Информация", f"Трек '{filename}' уже существует в папке 'music'.")

                # Проверяем, если трек уже в плейлисте, то добавляем его в список
                if filename not in self.playlist:
                    self.playlist.append(filename)  # Добавляем файл в список плейлиста
                    self.track_listbox.insert(END, sanitized_track_name)  # Отображаем в списке на интерфейсе
                    messagebox.showinfo("Добавлено", f'"{sanitized_track_name}" добавлена в плейлист!')
                else:
                    messagebox.showinfo("Информация", f"Трек '{sanitized_track_name}' уже в плейлисте.")
                return

            # Если файл не существует, пытаемся скачать его по URL
            downloaded = self.download_audio(track_url, filename)
            if downloaded:
                # Если скачивание прошло успешно, добавляем трек в плейлист
                self.playlist.append(filename)
                self.track_listbox.insert(END, sanitized_track_name)  # Отображаем в списке
                messagebox.showinfo("Добавлено", f'"{sanitized_track_name}" добавлена в плейлист!')
            else:
                # Если скачивание не удалось, показываем ошибку
                messagebox.showerror("Ошибка", f'Не удалось скачать трек "{track_name}".')
        else:
            # Локальный трек (не должен возникать, но на всякий случай)
            if track_url not in self.playlist:
                self.playlist.append(track_url)  # Добавляем трек в плейлист
                self.track_listbox.insert(END, track_url.replace('.mp3', ''))  # Отображаем в списке
                messagebox.showinfo("Добавлено", f'"{track_url.replace(".mp3", "")}" добавлена в плейлист!')
            else:
                messagebox.showinfo("Информация", f"Трек '{track_url.replace('.mp3', '')}' уже в плейлисте.")

    def download_audio(self, stream_url, filename):
        """Скачивание аудиофайла по URL и сохранение в папку music"""
        try:
            # Делаем GET запрос для скачивания аудиофайла
            response = requests.get(stream_url, stream=True)
            response.raise_for_status()  # Проверка на успешный ответ от сервера

            # Открываем файл в режиме записи (wb - write binary)
            with open(os.path.join(self.music_folder, filename), 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):  # Скачиваем файл кусками по 1024 байта
                    if chunk:
                        f.write(chunk)  # Записываем кусок в файл
            return True  # Возвращаем True, если скачивание прошло успешно
        except Exception as e:
            print(f"Ошибка загрузки аудио: {e}")  # Выводим ошибку в консоль
            return False  # Возвращаем False, если произошла ошибка

    def search_jamendo_tracks(self, query):
        """Поиск треков через Jamendo API"""
        url = "https://api.jamendo.com/v3.0/tracks/"  # URL API для поиска треков
        params = {
            "client_id": self.JAMENDO_CLIENT_ID,  # Ваш client_id
            "format": "json",  # Ответ в формате JSON
            "limit": 100,  # Ограничение на количество результатов
            "namesearch": query,  # Поисковый запрос
            "audioformat": "mp32",  # Используем 32 kbps для быстрого скачивания
            "include": "licenses"  # Включаем информацию о лицензиях
        }

        try:
            # Отправляем запрос к API с параметрами
            response = requests.get(url, params=params)
            response.raise_for_status()  # Проверка на успешный ответ
            data = response.json()  # Преобразуем ответ в JSON

            # Если в ответе есть результаты, возвращаем их
            if 'results' in data and data['results']:
                tracks = data['results']
                return tracks  # Возвращаем полные данные трека
            else:
                return []  # Если ничего не найдено, возвращаем пустой список

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к Jamendo API: {e}")
            messagebox.showerror("Ошибка", "Не удалось выполнить поиск через Jamendo API.")
            return []  # Если произошла ошибка, возвращаем пустой список

    def play_temp_track(self, track_name, track_url):
        """Загрузка и воспроизведение трека из временной директории, не добавляя его в плейлист"""
        # Санитируем имя трека, чтобы оно было безопасным для использования в пути файла
        sanitized_track_name = "".join([c if c.isalnum() or c in (' ', '_') else "_" for c in track_name])
        temp_file_path = os.path.join(self.temp_dir, f"{sanitized_track_name}.mp3")

        # Проверяем, если трек уже был загружен в темп директорию
        if not os.path.exists(temp_file_path):
            # Если файл не существует, скачиваем его
            downloaded = self.download_temp_audio(track_url, temp_file_path)
            if not downloaded:
                messagebox.showerror("Ошибка", f'Не удалось скачать трек "{track_name}".')
                return

        # Загружаем и воспроизводим трек
        self.load_and_play_temp_track(temp_file_path, track_name)
        self.current_track_name = track_name  # Сохраняем имя текущего трека

    def download_temp_audio(self, stream_url, temp_file_path):
        """Скачивание аудио для временного воспроизведения"""
        try:
            # Делаем GET запрос для скачивания аудиофайла
            response = requests.get(stream_url, stream=True)
            response.raise_for_status()

            # Сохраняем файл во временную директорию
            with open(temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return True  # Возвращаем True, если скачивание прошло успешно
        except Exception as e:
            print(f"Ошибка загрузки аудио: {e}")
            return False  # Возвращаем False, если произошла ошибка

    def load_and_play_temp_track(self, track_path, track_name):
        """Загружает и воспроизводит трек из временной директории"""
        # Загружаем и конвертируем аудиофайл в одномерный массив
        audio_segment = AudioSegment.from_mp3(track_path).set_channels(1)
        self.audio_samples = np.array(audio_segment.get_array_of_samples())

        # Если визуализатор существует, загружаем аудиосэмплы
        if self.audio_visualizer:
            self.audio_visualizer.load_samples(self.audio_samples)

        pygame.mixer.music.load(track_path)  # Загружаем файл в pygame для воспроизведения
        self.track_label.config(text=f"Playing: {track_name}")  # Обновляем текст
        self.track_length = pygame.mixer.Sound(track_path).get_length()  # Получаем длину трека
        self.end_time_label.config(text=self.format_time(self.track_length))  # Отображаем длительность
        self.progress_bar.set_progress(0)  # Сбрасываем прогресс
        self.start_time_label.config(text='00:00')  # Сбрасываем время начала

        # Запускаем воспроизведение
        pygame.mixer.music.play()
        self.is_playing_temp = True  # Устанавливаем флаг воспроизведения временного трека
        self.is_paused = False  # Сбрасываем флаг паузы

    def mp3_to_folder(self):
        """Метод для добавления MP3-файлов в папку с музыкой и плейлист"""
        file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])

        if not file_path:
            return

        # Получаем имя файла
        file_name = os.path.basename(file_path)

        # Проверяем, существует ли файл с таким именем в папке с музыкой
        if file_name in self.track_list:
            messagebox.showwarning("Предупреждение", "Этот трек уже находится в плейлисте")
            return

        # Копируем файл в папку с музыкой
        try:
            shutil.copy(file_path, self.music_folder)
            self.track_list.append(file_name)  # Добавляем в список треков
            self.playlist.append(file_name)  # Добавляем в плейлист

            # Обновляем Listbox
            track_display_name = file_name.replace('.mp3', '')
            self.track_listbox.insert(END, track_display_name)

            messagebox.showinfo("Успешно", "Трек успешно добавлен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить трек: {e}")

    def on_closing(self):
        """Обработчик закрытия окна"""
        self.is_playing = False  # Остановка воспроизведения

        # Проверяем, была ли запущена задача обновления прогресса
        if hasattr(self, 'update_progress_job'):
            self.root.after_cancel(self.update_progress_job)  # Остановка цикла обновления прогресса

        # Проверяем, была ли запущена задача обновления визуализации
        if hasattr(self, 'update_visualization_job'):
            self.root.after_cancel(self.update_visualization_job)  # Остановка цикла визуализации

        self.root.quit()  # Завершение основного цикла tkinter
        self.root.destroy()  # Закрытие основного окна
        pygame.mixer.quit()  # Завершение работы pygame


if __name__ == "__main__":
    root = Tk()
    app = MP3Player(root)
    root.mainloop()
    pygame.mixer.quit()  # Закрытие воспроизведения
