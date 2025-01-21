from rest_framework import viewsets
from main_app.seriailzers.habit import HabitSerializer


class HabbitView(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
