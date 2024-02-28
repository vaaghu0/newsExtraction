from rest_framework import generics
from .models import cas_document, cas_summary
from .serializer import documentSerializer, summarySerializer
from django.template import loader
from django.shortcuts import render
from .utils import scrapper
from django.http import HttpResponse
# Create your views here.

class DocumentList(generics.ListCreateAPIView):
  queryset = cas_document.objects.all()
  serializer_class = documentSerializer


class SummaryList(generics.ListCreateAPIView):
  queryset = cas_summary.objects.all()
  serializer_class = summarySerializer

def upload(request):
  context = {}
  if request.method == 'POST' and request.FILES.get('files'):
    file =  request.FILES.get('files')
    dataStream = scrapper.main(file, request.POST.get('password'))
    response = HttpResponse(dataStream, content_type='application/csv')
    response['Content-Disposition'] = 'attachment; filename='+"".join(file.name.split(".")[:-1])+'.csv'
    return response

  return render(request, "cas/upload.html", context)