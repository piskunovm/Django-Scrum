from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.forms import ModelForm

from authapp.models import User
from mainapp.models import Article


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", 'sex', 'age', "email", "avatar", "about_me"]
        # field_order = ["age", "name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            self.fields["username"].help_text = None


class PostCreationForm(ModelForm):
    body = forms.CharField(
        label="Текст статьи",
        widget=CKEditorUploadingWidget(config_name="article"),
    )

    class Meta:
        model = Article
        fields = ('title',
                  'preview',
                  'body',
                  'image',
                  'category',
                  'tag')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs = {"rows": 1}
        self.fields["tag"].widget.attrs = {"rows": 1}
        self.fields["preview"].widget.attrs = {"rows": 4}
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
