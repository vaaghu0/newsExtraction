from django.contrib import admin
from .models import cas_document, cas_summary

admin.site.register([cas_document, cas_summary])
