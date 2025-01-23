from rest_framework import serializers
from main_app.models.habit import Habit


class HabitSerializer(serializers.Serializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ["user", "start_date", "done"]
