from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.



class Article(models.Model):

		title = models.CharField(max_length=140)
		body  = models.TextField()
		auther = models.ForeignKey(User)
		submitted = models.DateTimeField(blank=True)
		
		def __unicode__(self):
				return self.title
		def save(self, **kwargs):
				self.submitted = datetime.now()
				super(Article, self).save()
