from django.db import models


# Create your models here.
class Translation(models.Model):
    input_text = models.TextField()
    output_text = models.TextField()
    from_user = models.CharField(max_length=255)
