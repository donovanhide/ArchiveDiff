from django.conf import settings
from celery.task import Task
import subprocess
import sys
import os
import csv
from models import *

class WarcIndexer(Task):
    name = "warc.index"

    def truncate_url(self,url):
        if len(url)>2000:
            print url
            return url[0:2000]
        return url

    def run(self,warc_path,**kwargs):
        logger = self.get_logger(**kwargs)

        indexerScript = os.path.join(settings.INDEXER_DIR,"run.sh")
        indexerCommand = "%s %s" % (indexerScript,warc_path)
        logger.info("Running command: %s" % indexerCommand)
        indexer =  subprocess.Popen(indexerCommand,stdout=subprocess.PIPE,shell=True)
        reader = csv.reader(indexer.stdout, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        rows=[]
        for row in reader:
            rows.append(row)

        logger.info("Adding WARC")
        for row in rows:
            sys.stdout.write('.')
            warc = row[0]
            break
        newWarc, created = Warc.objects.get_or_create(filename=warc, defaults={'filename':warc})

        logger.info("Adding Requests and Content Types")
        requests={}
        contentTypes = {}

        for row in rows:
            sys.stdout.write('.')
            url = self.truncate_url(row[1])
            if not requests.has_key(url):#Needed?
                newRequest, created = Request.objects.get_or_create(url=url, defaults = {'url':url})
                requests[url] = newRequest.id
            contentType = row[6]
            if not contentTypes.has_key(contentType):
                newContentType, created = ContentType.objects.get_or_create(name=contentType,defaults={'name': contentType})
                contentTypes[contentType] = newContentType.id

        logger.info("Deleting Responses associated with this Warc")
        Response.objects.filter(warc=newWarc).delete()

        logger.info("Adding Responses")
        for row in rows:
            sys.stdout.write('.')
            url = self.truncate_url(row[1])
            time = row[2]
            code = row[3]
            etag = row[4]
            last_modified = row[5]
            content_type= row[6]
            content_length = row[7]
            offset = row[8]
            hash = row[9]
            newResponse = Response(
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
                if time:
                    newResponse.time=time
                newResponse.save()
            except Exception, e:
                print e
                print row
        logger.info("Finished index")


