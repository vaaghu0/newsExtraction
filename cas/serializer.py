from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from .models import cas_document, cas_summary

class documentSerializer(serializers.ModelSerializer):
  class Meta:
    model = cas_document
    fields = ['id','name']

class summarySerializer(serializers.ModelSerializer):
  class Meta:
    model = cas_summary
    fields = ['fund','folio','closing_balance','invested','allocation','nav_date','advisor']