from django.db import models

class Login(models.Model):
    email = models.EmailField('Почтааа')
    password = models.CharField('Пар0ль', max_length=100)

    def __str__(self):
        return self.email