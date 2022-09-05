from django.db import models

from django.conf import settings
# Create your models here.

User = settings.AUTH_USER_MODEL

class Expense(models.Model):

    CATEGORY_CHOICES = [
        ('ONLINE_SERVICES', 'Online Services'),
        ('TRAVEL', 'Travel'),
        ('FOOD', 'Food'),
        ('RENT', 'Rent'),
        ('OTHER', 'Other')
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    description = models.TextField()
    amount = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.owner.get_full_name()}'s expenses for {self.date}"
