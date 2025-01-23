from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Habit(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField(auto_now=True)
    end_date = models.DateField()
    target = models.PositiveBigIntegerField()
    times_completed = models.PositiveBigIntegerField(default=0)
    done = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
