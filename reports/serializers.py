from rest_framework import serializers
from users.models import Program

class ProgramRevenueSerializer(serializers.ModelSerializer):
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    lessons_count = serializers.IntegerField()

    class Meta:
        model = Program
        fields = ['id', 'name', 'price_per_hour', 'total_revenue', 'lessons_count']

class LessonsStatsSerializer(serializers.Serializer):
    completed = serializers.IntegerField()
    canceled = serializers.IntegerField()
    avg_fill = serializers.FloatField()

class ProgramPopularitySerializer(serializers.ModelSerializer):
    popularity = serializers.IntegerField()
    completion_rate = serializers.FloatField()

    class Meta:
        model = Program
        fields = ['id', 'name', 'popularity', 'completion_rate']