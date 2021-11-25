from mainapp.helpers.article.article_audio import generate_article_audio


class PostFlow:
    def __init__(self, action, article=None):
        self.action = action
        self.article = article
        self.next_status = self.flow()

    def flow(self):
        try:
            if self.action == "publicate":
                return "moderation"
            elif self.action == "moderated":
                generate_article_audio(self.article)
                return "published"
            elif self.action == "correcting":
                return "correction"
            elif self.action == "archivate":
                return "archive"
            elif self.action == "delete":
                return "inactive"
        except ValueError:
            print("Error in post action. Check request")

    def __str__(self):
        return self.next_status
