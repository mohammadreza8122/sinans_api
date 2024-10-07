import dal.autocomplete
from service.models import HomeCareCategory

class YourModelAutocomplete(dal.autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return HomeCareCategory.objects.none()

        qs = HomeCareCategory.objects.all()

        if self.q:
            qs = qs.filter(title__icontains=self.q)

        return qs
