from django.db import models
class BaseModel(models.Model):
  is_deleted = models.BooleanField(default=False)
  
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  deleted_at = models.DateTimeField(null=True, blank=True)

  created_by = models.CharField(max_length=300)
  updated_by = models.CharField(max_length=300, null=True, blank=True)
  deleted_by = models.CharField(max_length=300, null=True, blank=True)

class CasDocument(BaseModel):
  name = models.CharField(250)
  password = models.TextField()

class CasSummary(BaseModel):
  fund = models.TextField()
  folio = models.TextField()
  closing_balance = models.FloatField()
  invested = models.FloatField()
  allocation = models.FloatField()
  nav_date = models.DateField()
  advisor = models.TextField()
  casDocument = models.ForeignKey(CasDocument, related_name = "summary")