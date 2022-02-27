import pyttsx3
import requests
from bs4 import BeautifulSoup
from kivy.lang.builder import Builder
from kivymd.app import MDApp
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.clipboard import Clipboard

class FirstWindow(Screen):
    ''' класс начального экрана (выбор бита ) '''

    # списки для хранения заголовков и ссылок на источник соответственно
    news_headlines = []
    news_links = []
    # словарь для хранения полного текста новости
    full_texts = dict()
    # специальный счетчик для ссылки на источник
    count = 9
    # переменные для воспроизведения музыки
    song_code = 0
    song = SoundLoader.load('Шурик.mp3')
    # объект библиотеки для озвучки текстов
    tts = pyttsx3.init()

    def spinner_click(self, value):
        ''' функция обработки меню выбора бита. Текст выбранной кнопки
        равен названию соответствующей мелодии '''
        self.song_name = str(value) + '.mp3'
        self.song_code = 1

    def play_song(self):
        ''' функция запуска бита. Мелодия будет играеть только
        в том случае, если было выбрано соответствующее название '''
        if self.song_code != 0:
            self.song = SoundLoader.load(self.song_name)
            self.song.volume = 0.5
            self.song.play()
            self.song.loop = True

    def parse(self):
        ''' Парсинг сайта. Заголовок новости сохраняется в
        список news_headlines
        Полный текст сохраняется в словарь full_texts,
        ссылка на сайт-источник сохраняется в список news_links '''
        url = 'http://breakingmad.me/ru/'
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'lxml')
        name_category = soup.find(class_="container")
        title = name_category.find_all("h2")
        news_text = name_category.find_all('div', class_='news-full-forspecial')
        links = soup.find_all('a')
        for num in range(10):
            self.news_headlines.append(title[num].text.strip())
            self.full_texts[title[num].text.strip()] = news_text[num].text.strip()
            try:
                # если есть ссылка на источник, сохраняем
                self.news_links.append(links[self.count].get('href'))
            except:
                # иначе сохраняем сообщение об ошибке
                self.news_links.append('Нет ссылки на источник!')
            self.count += 3
        # начальное значения для списка с ссылками
        self.count = 9

    def init_voice(self):
        ''' функция инициализации голоса озвучка. Выбор самого голоса и
        скорости речи '''
        voices = FirstWindow.tts.getProperty('voices')
        FirstWindow.tts.setProperty('voice', voices[0].id)
        FirstWindow.tts.setProperty("rate", 160)


class SecondWindow(Screen):
    ''' класс второго экрана (заголовок новости и переход на
    третий экран или начальный экран) '''

    # счетчик текущего заголовка
    count = 0

    def change_title(self):
        ''' функция смены заголовка '''
        
        current_title = self.manager.get_screen('second').count
        if self.manager.get_screen('second').count > 10:
            # если превысили кол-во новостей, обнуляем счетчик (cicle)
            self.ids.talk.text = FirstWindow.news_headlines[current_title]
            self.manager.get_screen('second').count = 0
        else:
            self.ids.talk.text = FirstWindow.news_headlines[current_title]
            self.manager.get_screen('second').count += 1

    def say_title(self):
        ''' функция озвучки заголовка '''
        text = self.ids.talk.text
        FirstWindow.tts.say(text)
        FirstWindow.tts.runAndWait()

    def stop_song(self):
        ''' функция остановки бита. Запускается одновременно с переходом
        на начальную страницу, поэтому необходимо обнулись все счетчики '''
        self.manager.get_screen('first').song.stop()
        self.manager.get_screen('first').song.unload()
        self.manager.get_screen('first').count = 9
        self.manager.get_screen('second').count = 0

    def show_full(self):
        ''' функция получения полного текста новости. Вызывается одновременно с
        переходом на третий экран '''
        self.manager.get_screen('third').ids.full.text = (
            FirstWindow.full_texts[FirstWindow.news_headlines[self.count - 1]])


class ThirdWindow(Screen):
    ''' класс последнего окна (полный текст новости и кнопка
    сохранения ссылки на источник) '''
    def get_link(self):
        ''' функция запоминания в буфер обмена ссылки на сайт-источник '''
        current_link = self.manager.get_screen('second').count - 1
        Clipboard.copy(FirstWindow.news_links[current_link])
        self.ids.link.text = 'Ссылка скопирована'


class WindowManager(ScreenManager):
    ''' пустой, но обязательный класс '''
    pass


class NovostockApp(MDApp):
    ''' класс самого приложения '''
    def build(self):
        ''' функция 'сборки' приложения. Передача логотипа и окон,
        описанных выше '''
        self.icon = "logo.png"
        Builder.load_file('new.kv')
        screen_manager = ScreenManager()
        screen_manager.add_widget(FirstWindow(name='first'))
        screen_manager.add_widget(SecondWindow(name='second'))
        screen_manager.add_widget(ThirdWindow(name='third'))
        return screen_manager

if __name__ == '__main__':
    NovostockApp().run()