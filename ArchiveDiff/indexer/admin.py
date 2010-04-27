from django.contrib import admin
from ArchiveDiff.indexer.models import Warc,Seed,Request,Response,ContentType

class ResponseAdmin(admin.ModelAdmin):
    list_display = ('request','warc','content_type','code','time','etag','last_modified','hash')

admin.site.register(Warc)
admin.site.register(Seed)
admin.site.register(Request)
admin.site.register(Response,ResponseAdmin)
admin.site.register(ContentType)
