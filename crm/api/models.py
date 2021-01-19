from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
import uuid


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Mail_Folder(BaseModel):
    id = models.AutoField(primary_key=True)
    folder_name = models.CharField(max_length=250)
    user = models.ForeignKey(User, related_name='folder_user', null=True,on_delete=models.DO_NOTHING)
    unread_count = models.PositiveIntegerField()
        
class Mail(BaseModel):
    id = models.AutoField(primary_key=True)
    from_user = models.ForeignKey(User, related_name='from_user', null=True,on_delete=models.DO_NOTHING)
    to_user = models.ForeignKey(User, related_name='to_user', null=True,on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, related_name='user', null=True,on_delete=models.DO_NOTHING)
    folder_name = models.CharField(max_length=100, default='inbox')
    category = models.CharField(max_length=100)
    subject = models.TextField(default='',null=True)
    content = models.TextField(default='',null=True)
    is_read = models.BooleanField(default=False)
    label = models.JSONField(default=list)


    
class Notification(BaseModel):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='notification_user', null=True,on_delete=models.DO_NOTHING)