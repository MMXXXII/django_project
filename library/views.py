
from django.views.generic import TemplateView
from typing import Any
from model_bakery import baker

from library.models import Library

# Create your views here.
class ShowLibraryView(TemplateView):
    template_name = "library/show_library.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['library'] = Library.objects.all()

        return context


