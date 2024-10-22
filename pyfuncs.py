#!/usr/bin/env python

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import re
import os
import sys
import urllib
import urllib2
import cookielib
import StringIO
import gzip
import urlparse
import cgi


def add_url_param(url, **params):
    n = 3
    parts = list(urlparse.urlsplit(url))
    d = dict(cgi.parse_qsl(parts[n]))  # use cgi.parse_qs for list values
    d.update(params)
    parts[n] = urllib.urlencode(d)
    return urlparse.urlunsplit(parts)


os.environ["PATH"] = os.environ["PATH"] + os.pathsep + \
    os.path.dirname(os.path.realpath(__file__)) + os.pathsep + os.getcwd()


def which_exec(execfile):
    for path in os.environ["PATH"].split(":"):
        if os.path.exists(path + "/" + execfile):
            return path + "/" + execfile


def listize(varlist):
    il = 0
    ix = len(varlist)
    ilx = 1
    newlistreg = {}
    newlistrev = {}
    newlistfull = {}
    while(il < ix):
        newlistreg.update({ilx: varlist[il]})
        newlistrev.update({varlist[il]: ilx})
        ilx = ilx + 1
        il = il + 1
    newlistfull = {1: newlistreg, 2: newlistrev,
                   'reg': newlistreg, 'rev': newlistrev}
    return newlistfull


def twolistize(varlist):
    il = 0
    ix = len(varlist)
    ilx = 1
    newlistnamereg = {}
    newlistnamerev = {}
    newlistdescreg = {}
    newlistdescrev = {}
    newlistfull = {}
    while(il < ix):
        newlistnamereg.update({ilx: varlist[il][0].strip()})
        newlistnamerev.update({varlist[il][0].strip(): ilx})
        newlistdescreg.update({ilx: varlist[il][1].strip()})
        newlistdescrev.update({varlist[il][1].strip(): ilx})
        ilx = ilx + 1
        il = il + 1
    newlistnametmp = {1: newlistnamereg, 2: newlistnamerev,
                      'reg': newlistnamereg, 'rev': newlistnamerev}
    newlistdesctmp = {1: newlistdescreg, 2: newlistdescrev,
                      'reg': newlistdescreg, 'rev': newlistdescrev}
    newlistfull = {1: newlistnametmp, 2: newlistdesctmp,
                   'name': newlistnametmp, 'desc': newlistdesctmp}
    return newlistfull


def arglistize(proexec, *varlist):
    il = 0
    ix = len(varlist)
    ilx = 1
    newarglist = [proexec]
    while(il < ix):
        if varlist[il][0] is not None:
            newarglist.append(varlist[il][0])
        if varlist[il][1] is not None:
            newarglist.append(varlist[il][1])
        il = il + 1
    return newarglist


def download_from_url(httpurl, httpheaders, httpcookie):
    geturls_opener = urllib2.build_opener(
        urllib2.HTTPCookieProcessor(httpcookie))
    geturls_opener.addheaders = httpheaders
    geturls_text = geturls_opener.open(httpurl)
    if(geturls_text.info().get("Content-Encoding") == "gzip" or geturls_text.info().get("Content-Encoding") == "deflate"):
        strbuf = StringIO.StringIO(geturls_text.read())
        gzstrbuf = gzip.GzipFile(fileobj=strbuf)
        out_text = gzstrbuf.read()[:]
    if(geturls_text.info().get("Content-Encoding") != "gzip" and geturls_text.info().get("Content-Encoding") != "deflate"):
        out_text = geturls_text.read()[:]
    return out_text
