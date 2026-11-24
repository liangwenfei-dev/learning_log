from django.db import models
from django.contrib.auth.models import User
# 先注释这两行
# from django.db.models.signals import post_save
# from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True, verbose_name="个人简介")  # 新增这一行

    def __str__(self):
        return f"{self.user.username}的个人资料"

# 注释整个信号
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
