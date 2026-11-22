import os
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image
from .models import Topic, Entry
from ckeditor.widgets import CKEditorWidget

# 封面图允许的格式与大小上限（2MB）
ALLOWED_IMAGE_EXT = ['jpg', 'jpeg', 'png', 'gif', 'webp']
MAX_IMAGE_SIZE = 2 * 1024 * 1024


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text', 'image']
        labels = {'text': '主题名称', 'image': '封面图'}
        help_texts = {'image': '支持 JPG、PNG、GIF、WEBP 格式，大小不超过 2MB。'}
        widgets = {'image': forms.ClearableFileInput(attrs={'class': 'form-control'})}

    def clean_image(self):
        """校验上传的封面图：格式、大小、是否为真实图片。"""
        img = self.cleaned_data.get('image')
        if not img:
            return img

        # 编辑主题时未重新选择图片，拿到的是已保存的旧图片，不重复校验
        if getattr(img, '_committed', False):
            return img

        # 1. 校验扩展名
        ext = os.path.splitext(img.name)[1].lower().lstrip('.')
        if ext not in ALLOWED_IMAGE_EXT:
            raise ValidationError('只支持 JPG、PNG、GIF、WEBP 格式的图片。')

        # 2. 校验大小
        if img.size > MAX_IMAGE_SIZE:
            raise ValidationError(f'图片大小不能超过 2MB（当前 {img.size / 1024 / 1024:.1f}MB）。')

        # 3. 校验文件内容确实是一张图片（防止改后缀上传其他文件）
        try:
            with Image.open(img) as im:
                im.verify()
            img.seek(0)  # 校验后把文件指针复位，便于后续保存
        except Exception:
            raise ValidationError('上传的文件不是有效的图片，请更换后再试。')

        return img


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': '笔记内容'}
        widgets = {'text': CKEditorWidget()}
