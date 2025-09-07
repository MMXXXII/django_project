from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views import View 


from library.models import Library

# Create your views here.
class ShowLibraryView(View):
    def get(request, *args, **kwargs):
        library = Library.objects.all()

        result = ""
        for s in library:
            result += s.name + "<br>"
        
        return HttpResponse(result)
    