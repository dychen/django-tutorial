from django.db import models

class Pokemon(models.Model):
    name = models.CharField(max_length=50)
    number = models.PositiveIntegerField()
    type = models.CharField(max_length=50)