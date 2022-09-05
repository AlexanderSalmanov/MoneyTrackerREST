from django.db import models

from django.conf import settings
# Create your models here.

User = settings.AUTH_USER_MODEL

class Income(models.Model):

    SOURCE_CHOICES = (
        ('SALARY', 'Salary'),
        ('BUSINESS', 'Business'),
        ('HUSTLE', 'Hustle'),
        ('OTHER', 'Other')
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    description = models.TextField()
    source = models.CharField(max_length=40, choices=SOURCE_CHOICES)
    date = models.DateField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.owner.get_full_name()}'s income for {self.date}"
