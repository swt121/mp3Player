import pygame
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from ScrollBarDesign import CustomScrollbar


class SearchWindow:
    def __init__(self, root, player):
        """
        Инициализация окна поиска

        Args:
        root: Основное окно;
        player: Объект MP3-плеера, обеспечивающий функциональность.
        """
        self.root = root  # Ссылка на основное окно
        self.player = player  # Ссылка на объект MP3-плеера
        self.search_window = Toplevel(root)  # Создаем дочернее окно
        self.search_window.title("Search")  # Устанавливаем заголовок окна
        self.search_window.geometry("400x400")  # Размеры окна

        self.all_tracks = []  # Список всех найденных треков
        self.is_playing = False  # Переменная для отслеживания состояния воспроизведения
        self.current_index = 0  # Индекс текущего трека

        # Надпись для поля поиска
        self.label = Label(self.search_window, text="Search for tracks:", font=("Helvetica", 12))
        self.label.pack(pady=10)

        # Фрейм для поля ввода и кнопки
        self.search_frame = Frame(self.search_window)
        self.search_frame.pack(pady=5)

        # Поле ввода для запроса
        self.query_entry = Entry(self.search_frame, width=30, font=("Helvetica", 10))
        self.query_entry.pack(side=LEFT, padx=20)

        # Изображения для кнопок добавления трека
        self.photo_add = ImageTk.PhotoImage(
            Image.open("pics//add.png").resize((30, 30)))
        self.photo_add_night = ImageTk.PhotoImage(
            Image.open("pics//add_night.png").resize((30, 30)))

        # Кнопка для выполнения поиска
        self.search_button = Button(self.search_frame, command=self.search_tracks,
                                    image=self.player.photo_search, borderwidth=0, cursor='hand2')
        self.search_button.pack(side=RIGHT)

        # Фрейм для размещения кнопок добавления и воспроизведения
        self.button_frame = Frame(self.search_window)
        self.button_frame.pack(pady=5)

        # Кнопка для добавления выбранного трека
        self.add_button = Button(self.button_frame, command=self.add_selected_track,
                                 image=self.photo_add, borderwidth=0, cursor='hand2')
        self.add_button.pack(side=LEFT, padx=10)

        # Кнопка для переключения воспроизведения и паузы
        self.play_button = Button(self.button_frame, command=self.toggle_play_pause, borderwidth=0,
                                  image=self.player.photo_play, cursor='hand2')
        self.play_button.pack(side=RIGHT)

        self.results_frame = Frame(self.search_window)
        self.results_frame.pack(fill=BOTH, expand=True)

        # Фрейм для отображения результатов поиска
        self.results_listbox = Listbox(self.results_frame, selectmode=SINGLE, activestyle='none')
        self.results_listbox.pack(side=LEFT, fill=BOTH, expand=True)

        # Создаем кастомный скроллбар и добавляем его к Listbox
        self.scrollbar = CustomScrollbar(self.results_frame, self.results_listbox, bg_color='#f0f0f0',
                                         slider_color='#909090')
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Привязка клавиш для управления
        self.results_listbox.bind('<Up>', self.on_arrow_up)
        self.results_listbox.bind('<Down>', self.on_arrow_down)
        self.query_entry.bind('<Return>', self.on_enter_search_tracks)

        # Устанавливаем первый трек как выбранный по умолчанию
        self.results_listbox.selection_set(0)
        self.results_listbox.focus_set()  # Устанавливаем фокус на Listbox

        # Установка темы
        if self.player.is_day_theme:
            self.set_day_mode_search()
        else:
            self.set_night_mode_search()

    def search_tracks(self):
        """Выполняет поиск треков через Jamendo API по введенному запросу"""
        query = self.query_entry.get()  # Получаем запрос из поля ввода
        if not query:
            messagebox.showerror("Ошибка", "Введите поисковый запрос.")
            return

        self.results_listbox.delete(0, END)  # Очищаем список выданных треков
        self.all_tracks = []
        tracks = self.player.search_jamendo_tracks(query)  # Получаем результаты поиска через API

        if tracks:
            for track in tracks:
                track_name = track.get("name", "Unknown Title")  # Название трека
                artist_name = track.get("artist_name", "Unknown Artist")  # Имя исполнителя
                self.results_listbox.insert(END, f"{track_name} - {artist_name}")
                self.all_tracks.append(track_name)
            self.tracks_data = tracks  # Сохраняем данные для добавления
        else:
            messagebox.showinfo("Результаты поиска", "Ничего не найдено.")

    def add_selected_track(self):
        """Добавляет выбранный трек из списка результатов в плейлист"""
        selection = self.results_listbox.curselection()  # Получаем текущий выбор трека
        if not selection:
            messagebox.showerror("Ошибка", "Выберите трек для добавления.")
            return

        self.current_index = selection[0]
        selected_track = self.tracks_data[self.current_index]  # Данные выбранного трека
        track_name = selected_track.get("name", "Unknown Title")
        track_url = selected_track.get("audio", "")  # Ссылка на трек

        # Добавляем трек в плейлист MP3-плеера
        self.player.add_track_to_playlist(track_name, track_url)

    def on_arrow_up(self, event):
        """Навигация по трекам стрелкой вверх"""
        # Проверяем, что текущий индекс не равен нулю, иначе переходим в конец списка
        if self.current_index > 0:
            # Если текущий трек не первый, уменьшаем индекс на 1
            self.current_index -= 1
        else:
            # Если первый трек, устанавливаем индекс на последний трек
            self.current_index = len(self.all_tracks) - 1

        # Обновляем выделение в списке треков
        self.update_selection()

    def on_arrow_down(self, event):
        """Навигация по трекам стрелкой вниз"""
        # Проверяем, что текущий индекс не равен последнему треку
        if self.current_index < len(self.all_tracks) - 1:
            # Если текущий трек не последний, увеличиваем индекс на 1
            self.current_index += 1
        else:
            # Если последний трек, устанавливаем индекс на первый трек
            self.current_index = 0

        # Обновляем выделение в списке треков
        self.update_selection()

    def update_selection(self):
        """Обновление выделения в списке треков"""
        self.results_listbox.selection_clear(0, END)  # Снять выделение со всех треков
        self.results_listbox.selection_set(self.current_index)  # Установить выделение на текущем треке
        self.results_listbox.activate(self.current_index)  # Сделать текущий трек активным

    def on_enter_search_tracks(self, event):
        """Выполняет поиск при нажатии клавиши Enter"""
        self.search_tracks()

    def toggle_play_pause(self):
        """Переключает воспроизведение и паузу для выбранного трека."""
        selection = self.results_listbox.curselection()  # Получаем текущий выбор трека
        if not selection:
            messagebox.showerror("Ошибка", "Выберите трек для воспроизведения.")
            return

        selected_track = self.tracks_data[selection[0]]
        track_name = selected_track.get("name", "Unknown Title")
        track_url = selected_track.get("audio", "")

        # Проверяем, воспроизводится ли выбранный трек или другой
        if self.player.is_playing_temp and not self.player.is_paused:
            if self.player.current_track_name == track_name:
                # Пауза текущего трека
                pygame.mixer.music.pause()
                self.player.is_paused = True

                if self.player.is_day_theme:
                    self.play_button.config(image=self.player.photo_play)
                else:
                    self.play_button.config(image=self.player.photo_play_night)

            else:
                # Остановить текущий трек и воспроизвести новый
                pygame.mixer.music.stop()
                self.player.is_playing_temp = False
                self.player.play_temp_track(track_name, track_url)  # Воспроизводим новый трек

                if self.player.is_day_theme:
                    self.play_button.config(image=self.player.photo_pause)
                else:
                    self.play_button.config(image=self.player.photo_pause_night)

        elif self.player.is_playing_temp and self.player.is_paused:
            # Если трек на паузе, продолжаем воспроизведение с того же места
            pygame.mixer.music.unpause()
            self.player.is_paused = False

            if self.player.is_day_theme:
                self.play_button.config(image=self.player.photo_pause)
            else:
                self.play_button.config(image=self.player.photo_pause_night)

        else:
            # Воспроизводим выбранный трек, если никакой не играет
            self.player.play_temp_track(track_name, track_url)

            if self.player.is_day_theme:
                self.play_button.config(image=self.player.photo_pause)
            else:
                self.play_button.config(image=self.player.photo_pause_night)

    def set_day_mode_search(self):
        self.search_window.config(bg='#f0f0f0')
        self.results_listbox.config(bg='#f0f0f0', selectbackground='lightgray', fg='black',
                                    selectforeground='black')
        self.play_button.config(bg='#f0f0f0', image=self.player.photo_play, activebackground='#f0f0f0')
        self.search_frame.config(bg='#f0f0f0')
        self.button_frame.config(bg='#f0f0f0')
        self.add_button.config(bg='#f0f0f0', image=self.photo_add, activebackground='#f0f0f0')
        self.query_entry.config(bg='#f0f0f0', fg='black')
        self.search_button.config(bg='#f0f0f0', image=self.player.photo_search, activebackground='#f0f0f0')
        self.label.config(bg='#f0f0f0', fg='black')
        self.scrollbar.set_bg_color('#f0f0f0')
        self.scrollbar.set_slider_color('#909090', hover_color='#707070')

    def set_night_mode_search(self):
        self.search_window.config(bg='#302d38')
        self.results_listbox.config(bg='#302d38', selectbackground='#201e26', fg='white',
                                    selectforeground='white')
        self.play_button.config(bg='#302d38', image=self.player.photo_play_night, activebackground='#302d38')
        self.search_frame.config(bg='#302d38')
        self.button_frame.config(bg='#302d38')
        self.add_button.config(bg='#302d38', image=self.photo_add_night, activebackground='#302d38')
        self.query_entry.config(bg='#302d38', fg='white')
        self.search_button.config(bg='#302d38', activebackground='#302d38', image=self.player.photo_search_night)
        self.label.config(bg='#302d38', fg='white')
        self.scrollbar.set_bg_color('#302d38')
        self.scrollbar.set_slider_color('#201e26', hover_color='#1f2129')

    def update_theme(self):
        if self.player.is_day_theme:
            self.set_night_mode_search()
        else:
            self.set_day_mode_search()
