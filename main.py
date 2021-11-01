import pyttsx3
import requests
from bs4 import BeautifulSoup
from kivy.lang.builder import Builder
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

Window.size = (720, 720)
Window.clearcolor = (1, 1, 1, 1)

tts = pyttsx3.init()
voices = tts.getProperty('voices')
tts.setProperty('voice', voices[0].id)
tts.setProperty("rate", 130)

class FirstWindow(Screen):
    news = []
    song = SoundLoader.load('Шурик.mp3')
    song_code = 0
    song_name = ''

    def spinner_click(self, value):
        self.song_name = str(value) + '.mp3'
        if value == 'Шурик':
            self.song_code = 1
        elif value == 'Биография':
            self.song_code = 2
        elif value == 'Чебурашка':
            self.song_code = 3   

    def play_song(self):
        self.song = SoundLoader.load(self.song_name)
        self.song.volume = 0.45
        self.song.play()   

    def parse(self):
        url = 'http://breakingmad.me/ru/'
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'lxml')
        name_category = soup.find(class_="container")
        children = name_category.findChildren("h2")
        for child in children:
            title = str(child)
            self.news.append(title[4 : len(title) - 5])        


class SecondWindow(Screen):
    count = 0

    def change_title(self):
        if self.count > 11:
            self.count = 0
        else:    
            button_link = ObjectProperty()    
            self.button_link.text = FirstWindow().news[self.count]
            self.count += 1  

    def say_title(self):
        button_link = ObjectProperty()
        text = self.button_link.text
        tts.say(text)
        tts.runAndWait()

    def stop_song(self):
        FirstWindow().song.stop()     
        FirstWindow().song.unload()   

class WindowManager(ScreenManager):
    pass

kv = Builder.load_file('new.kv')
       
class NovostockApp(App):
    def build(self):
        return kv

if __name__ == '__main__':
    NovostockApp().run()