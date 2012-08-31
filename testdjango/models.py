from django.db import models

class FacebookUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50)
    description = models.TextField(null=True)
    about = models.TextField(null=True)
    is_published = models.NullBooleanField(null=True)
    website = models.CharField(max_length=100, null=True)
    link = models.CharField(max_length=100, null=True)
    number = models.PositiveIntegerField(null=True)
    talking_about_count = models.IntegerField(null=True)
    likes = models.IntegerField(null=True)

    def __unicode__(self):
        return self.name