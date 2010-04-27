from django.shortcuts import render_to_response
from org.archive.io.warc import WARCReaderFactory
from org.apache.commons.httpclient import Header,HttpParser,StatusLine
from org.apache.commons.httpclient.util import EncodingUtil, DateUtil
from django.conf import settings
from django.db import IntegrityError
import os,glob, datetime
from jarray import zeros, array
from models import *

def list(request):
    warcs = []
    for warc in glob.glob(os.path.join(settings.WARC_DIR, '*.warc.gz')):
        warcs.append(warc)
    return render_to_response('indexer/list.html', {"warcs": warcs},
                              mimetype="text/html")

def process(request):
    path = request.GET['path']
    warc,created = Warc.objects.get_or_create(filename=path, defaults={
                            'filename':path
                    })
    if not created:
        Response.objects.filter(warc=warc).delete()

    reader = WARCReaderFactory.get(path)

    content_types = set(ContentType.objects.values_list('name', flat=True))
    print "Processing Content Types"
    for record in reader:
        header = record.getHeader()
        if header.getHeaderValue('WARC-Type') == 'response':
            httpHeaders = HttpParser.parseHeaders(record).tolist()
            content_type = getHeader(httpHeaders,'Content-Type')
            content_types.add(content_type)
    for content_type in  content_types:
        if content_type != None:
            content_type, created = ContentType.objects.get_or_create(name = content_type,defaults={
                                    'name' : content_type
                    })
            
    content_types = ContentType.objects.values()

    print "Processing headers"
    reader = WARCReaderFactory.get(path)
    for record in reader:
        header = record.getHeader()
        try:
            if header.getHeaderValue('WARC-Type') == 'response':
                request, created = Request.objects.get_or_create(url = header.getUrl(),defaults={
                                        'url':header.getUrl()
                                    })
                statusBytes =  HttpParser.readRawLine(record)
                statusString = ''.join(chr(c) for c in statusBytes)
                if (statusString and StatusLine.startsWithHTTP(statusString)):
                    statusLine = StatusLine(statusString)
                    httpHeaders = HttpParser.parseHeaders(record).tolist()
                    code = int(statusLine.getStatusCode())
                    date = parseDate(getHeader(httpHeaders,'Date'))
                    etag = getHeader(httpHeaders,'ETag')
                    last_modified = parseDate(getHeader(httpHeaders,'Last-Modified'))
                    content_length = header.getHeaderValue('Content-Length')
                    offset = header.getHeaderValue('Content-Length')
                    hash = header.getHeaderValue('WARC-Payload-Digest')
                    contentType = getHeader(httpHeaders,'Content-Type')

                    content_type = content_types.filter(name=contentType)

                    response = Response(
                                            request        = request,
                                            warc           = warc,
                                            code           = code,
                                            time           = date,
                                            etag           = etag,
                                            hash           = hash,
                                            last_modified  = last_modified,
                                            content_length = content_length,
                                            offset        = offset
                                        )
                    response.content_type_id   = content_type[0]['id']
                    response.save()
        except IntegrityError, e:   #which Error!!!
            print e
            print header
        except IndexError, e:
            print e
            print header
    return render_to_response('indexer/process.html', {"warc": reader},
                              mimetype="text/html")

def getHeader(headers,key):
    values = [h for h in headers if h.getName() == key]
    if len(values)>0:
        return values[0].getValue()
    return None;

def parseDate(date):
    if date:
        return datetime.datetime.fromtimestamp(DateUtil.parseDate(date).getTime()//1000)
    return None