from django.db import models

class Warc(models.Model):
    filename = models.CharField(max_length=200, db_index=True)

    def __unicode__(self):
        return self.filename

class Seed(models.Model):
    url = models.URLField(db_index=True)

    def __unicode__(self):
        return self.url

class Request(models.Model):
    seed = models.ForeignKey(Seed, null=True, blank=True)
    url = models.URLField(max_length=2000, db_index=True)

    def __unicode__(self):
        return self.url

class ContentType(models.Model):
    name = models.CharField(max_length=200, db_index=True)

    def __unicode__(self):
        return self.name

class Response(models.Model):
    request = models.ForeignKey(Request, editable=False)
    content_type = models.ForeignKey(ContentType,editable=False)
    warc = models.ForeignKey(Warc,editable=False)
    code = models.IntegerField(db_index=True)
    time = models.DateTimeField(db_index=True)
    etag = models.CharField(max_length=200,null=True,blank=True)
    hash = models.CharField(max_length=200)
    last_modified = models.DateTimeField(null=True,blank=True)
    content_length = models.IntegerField()
    offset = models.IntegerField()

    def request_url(self):
        return self.request.url

    def __unicode__(self):
        return "%s %s" % (self.code,self.time)
