from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Company(BaseModel):
    name = models.CharField(max_length = 200)
    symbol = models.CharField(max_length = 50)

    def __str__(self) -> str:
        return self.name + " -> " + self.symbol
    class Meta:
        db_table = "company"
        verbose_name = "company"
        verbose_name_plural = "companies"


class News(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    source = models.URLField()
    content = models.TextField()
    author = models.CharField(max_length=200)
    scheduled = models.DateTimeField(null=True)
    company = models.ForeignKey(Company,on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        db_table = "news"
        verbose_name = "news"
        verbose_name_plural = "news"

# class Embedding(BaseModel):
    