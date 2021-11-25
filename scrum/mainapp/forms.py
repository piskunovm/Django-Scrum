from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.forms import ModelForm

from .models import Comments


# Форма для комментария
class Add_Comment_Form(ModelForm):
    comment_text = forms.CharField(label='Написать комментарий',
                                   widget=CKEditorUploadingWidget(
                                       config_name='comment'))

    class Meta:
        model = Comments
        fields = ("comment_text",)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'comment-field'
            field.widget.attrs['placeholder'] = 'Ваш комментарий...'
            field.widget.attrs['name'] = 'text'
            self.fields['comment_text'].label = False






