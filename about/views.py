from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import (
    TeamSerializer,
    Team,
    Support,
    SupportSerializer,
    About,
    AboutSerializer,
)


class AboutAPIView(RetrieveAPIView):
    serializer_class = AboutSerializer
    queryset = About.objects.all()

    def get_object(self):
        return self.get_queryset().last()


class TeamAPIView(ListAPIView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()


class SupportAPIView(ListAPIView):
    serializer_class = SupportSerializer
    queryset = Support.objects.all()
