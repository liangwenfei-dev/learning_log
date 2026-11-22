from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    """用户的学习主题"""
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='topic_covers/',blank=True,null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        """返回模型的字符串表示"""
        return self.text 

class Entry(models.Model):
    """某个主题下的条目"""
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    

    class Meta:
        verbose_name_plural = "entries"

    def __str__(self):
        return f"{self.text[:50]}"