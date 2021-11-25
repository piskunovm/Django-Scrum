from mainapp.models import Score


def get_count_post_likes(post_id):
    return Score.objects.filter(article_id=post_id, score="like").count()


def get_count_post_dislikes(post_id):
    return Score.objects.filter(article_id=post_id, score="dislike").count()


class Liked:
    """Класс возвращает переменные для верстки"""

    @staticmethod
    def color_to_attr(color):
        if color:
            return "green"
        else:
            return "black"

    def __init__(self, color=None, text=None, obj=None):
        self.color = self.color_to_attr(color)
        self.text = text
        self.obj = obj

    # def __str__(self):
    #     return self.text


class Disliked:
    """Класс возвращает переменные для верстки"""

    @staticmethod
    def color_to_attr(color):
        if color:
            return "red"
        else:
            return "black"

    def __init__(self, color=None, text=None, obj=None):
        self.color = self.color_to_attr(color)
        self.text = text
        self.obj = obj

    # def __str__(self):
    #     return self.text
