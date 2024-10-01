from rest_framework import serializers
from .models import Team, Support, About, AboutSection, Statistic


class TeamSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "image" in representation and representation["image"]:
            representation["image"] = str(instance.image.url)[1:]

        return representation

    class Meta:
        model = Team
        fields = "__all__"


class SupportSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "image" in representation and representation["image"]:
            representation["image"] = str(instance.image.url)[1:]

        return representation

    class Meta:
        model = Support
        fields = "__all__"


class StatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistic
        fields = "__all__"


class AboutSectionSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "image" in representation and representation["image"]:
            representation["image"] = str(instance.image.url)[1:]

        return representation

    class Meta:
        model = AboutSection
        fields = "__all__"


class AboutSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()

    def get_sections(self, obj):
        return AboutSectionSerializer(obj.sections.all(), many=True).data

    def get_statistics(self, obj):
        return StatisticSerializer(obj.statistics.all(), many=True).data

    class Meta:
        model = About
        fields = "__all__"
