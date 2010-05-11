from django.conf import settings
from celery.task import Task
import subprocess
import sys
import os
import csv
from models import *

class WarcIndexer(Task):
    name = "warc.index"

    def run(self,warc_path,**kwargs):
        indexerCommand = os.path.join(settings.INDEXER_DIR,"run.sh")
        indexer =  subprocess.Popen("%s %s" % (indexerCommand,warc_path),stdout=subprocess.PIPE,shell=True)
        reader = csv.reader(indexer.stdout, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        rows=[]
        for row in reader:
            rows.append(row)

        print "Adding WARC"
        for row in rows:
            sys.stdout.write('.')
            warc = row[0]
            break
        newWarc, created = Warc.objects.get_or_create(filename=warc, defaults={'filename':warc})

        print "Adding Requests and Content Types"
        requests={}
        contentTypes = {}

        for row in rows:
            sys.stdout.write('.')
            url = row[1]
            if not requests.has_key(url):#Needed?
                newRequest, created = Request.objects.get_or_create(url=url, defaults = {'url':url})
                requests[url] = newRequest.id
            contentType = row[6]
            if not contentTypes.has_key(contentType):
                newContentType, created = ContentType.objects.get_or_create(name=contentType,defaults={'name': contentType})
                contentTypes[contentType] = newContentType.id

        print "Deleting Responses associated with this Warc"
        Response.objects.filter(warc=newWarc).delete()

        print "Adding Responses"
        for row in rows:
            sys.stdout.write('.')
            url = row[1]
            date = row[2]
            code = row[3]
            etag = row[4]
            last_modified = row[5]
            content_type= row[6]
            content_length = row[7]
            offset = row[8]
            hash = row[9]
            newResponse = Response(
                                        time=date,
                                        warc=newWarc,
                                        code=code,
                                        etag=etag,
                                        content_length=content_length,
                                        offset=offset,
                                        hash=hash
                                    )
            try:
                newResponse.content_type_id = contentTypes[content_type]
                newResponse.request_id = requests[url]
                if last_modified:
                    newResponse.last_modified=last_modified
                newResponse.save()
            except Exception, e:
                print e
                print row
        sys.stdout.flush()

