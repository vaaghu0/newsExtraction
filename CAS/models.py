from django.db import models
import uuid
class BaseModel(models.Model):
  is_deleted = models.BooleanField(default=False)
  
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  deleted_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    abstract = True

class cas_document(BaseModel):
  id = models.UUIDField(primary_key = True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length = 250)
  # password = models.CharField(max_length = 200)
  class Meta:
    db_table = "cas_documents"
    verbose_name = "Document"
    verbose_name_plural = "Documents"

class cas_summary(BaseModel):
  id = models.UUIDField(primary_key = True, default=uuid.uuid4, editable=False)
  fund = models.TextField()
  closing_balance = models.FloatField()
  current_value = models.FloatField()
  invested = models.FloatField()
  allocation = models.FloatField()
  folio = models.TextField(blank = True, null=True)
  nav_date = models.DateField(blank = True, null=True)
  advisor = models.CharField(max_length = 100,blank = True, null=True)
  document = models.ForeignKey(cas_document, related_name = "summary", on_delete=models.CASCADE)

  class Meta:
    db_table = "cas_summary"
    verbose_name = "Summary"
    verbose_name_plural = "Summaries"
