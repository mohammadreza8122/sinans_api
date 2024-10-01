from django.contrib import admin
from .models import Team, Support, About, AboutSection, Statistic


class AboutSectionInline(admin.StackedInline):
    model = AboutSection
    extra = 1


class StatisticInline(admin.TabularInline):
    model = Statistic
    extra = 1


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    inlines = (AboutSectionInline, StatisticInline)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "title")
    list_filter = ("name", "title")


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ("name", "title")
    list_filter = ("name", "title")
