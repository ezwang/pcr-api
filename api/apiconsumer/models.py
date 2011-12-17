from django.db import models

class APIConsumer(models.Model):
  name = models.CharField(max_length=200, unique=True)
  email = models.EmailField(max_length=75, unique=True)
  description = models.TextField()
  token = models.CharField(max_length=200, unique=True)
  permission_level = models.IntegerField()

  # 0 - no access, equivalent to no key
  # 1 - access to public data only
  # 2 - access to PCR data
  # 9001 - access to secret pcrsite stuff

  @property
  def valid(self):
    return self.permission_level > 0

  @property
  def access_pcr(self):
    return self.permission_level >= 2

  @property
  def access_secret(self):
    return self.permission_level > 9000
  
  def __unicode__(self):
    return "%s (level %d)" % (self.name, self.permission_level)
