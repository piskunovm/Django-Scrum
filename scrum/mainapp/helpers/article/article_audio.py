import os
import threading

import pyttsx3
from gtts import gTTS

from mainapp.helpers.article.article import get_article
from scrum.settings import ARTICLE_AUDIO_ROOT


class SaveArticleAudio(threading.Thread):
    def __init__(self, article):
        super(SaveArticleAudio, self).__init__()
        self.language = 'ru'
        self.article = article
        try:
            os.mkdir(ARTICLE_AUDIO_ROOT)
        except OSError:
            pass

    def run(self):
        if self.article.audio_name == 'generating':
            print(f'Аудиофайл для статьи "{self.article}" уже формируется.')
        elif self.article:
            # time.sleep(5)
            audio_name = f'article-{self.article.pk}.mp3'
            path = os.path.join(ARTICLE_AUDIO_ROOT, audio_name)
            try:
                os.remove(path)
            except OSError as err:
                pass
            text = self.article.body_for_search
            save_audio_name(self.article, 'generating')
            try:
                get_audio_gtts(text, path, self.language)
                save_audio_name(self.article, audio_name)
            except:
                try:
                    get_audio_pyttsx3(text, path)
                    save_audio_name(self.article, audio_name)
                except:
                    save_audio_name(self.article, 'error')
            print(f'Аудиофайл {audio_name} сформирован')


def generate_article_audio(article):
    th = SaveArticleAudio(article)
    th.setDaemon(True)
    th.start()


def save_audio_name(article, audio_name):
    article = get_article(article.pk)
    article.audio_name = audio_name
    article.save()


def get_audio_gtts(text, path, language):
    audio = gTTS(text=text, lang=language, slow=False)
    audio.save(path)


def get_audio_pyttsx3(text, path):
    tts = pyttsx3.init()
    tts.setProperty('voice', 'ru')
    tts.save_to_file(text=text, filename=path)
    tts.runAndWait()


def get_article_audio_url(article_pk):
    article = get_article(article_pk)
    return os.path.join(ARTICLE_AUDIO_ROOT, article.audio_name)
