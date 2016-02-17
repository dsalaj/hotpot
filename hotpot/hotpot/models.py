from django.db import models

class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2047)
    category = models.ForeignKey('Category')
    unit_price = models.DecimalField(decimal_places=2, max_digits=6)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name