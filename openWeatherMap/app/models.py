from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='city', null=True)
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        for field_name in ['name']:
            val = getattr(self, field_name, False)
            if val:
                setattr(self, field_name, val.capitalize())
        super(City, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'cities'


class Info(models.Model):
    extended = models.BooleanField(default=True)
    def __bool__(self):
        return self.extended
