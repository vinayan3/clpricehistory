from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)    
    price = models.IntegerField(null=True, blank=True)
    neighborhood = models.CharField(max_length=200, null=True)
    subCraigsList = models.CharField(max_length=200)
    section = models.CharField(max_length=200)
    date = models.DateTimeField()
    def __unicode__(self):
        return "CL City: %s Section:%s Posted: %s %s %i %s" % (
            self.subCraigsList,
            self.section,
            str(self.date),
            self.title,
            self.price if self.price is not None else 0,
            self.neighborhood if self.neighborhood is not None else "")
