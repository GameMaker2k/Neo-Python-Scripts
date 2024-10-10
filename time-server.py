#!/usr/bin/env python

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.
    Copyright 2016 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2016 Kazuki Przyborowski - https://github.com/KazukiPrzyborowski
    $FileInfo: time-server.py - Last Update: 3/16/2016 Ver. 0.0.1 RC 1  - Author: cooldude2k $
'''

import argparse
import datetime
import time

import cherrypy

parser = argparse.ArgumentParser(description="Test Time Server.")
parser.add_argument("--ver", "--version", action="version",
                    version="Test Time Server 0.0.1")
parser.add_argument("--port", "--port-number", default=4123,
                    help="port number to use for server.")
parser.add_argument("--host", "--host-name",
                    default="127.0.0.1", help="host name to use for server.")
parser.add_argument("--verbose", "--verbose-mode",
                    help="show log on terminal screen.", action="store_true")
parser.add_argument("--gzip", "--gzip-mode",
                    help="enable gzip http requests.", action="store_true")
parser.add_argument("--gzipfilter", "--gzipfilter-mode",
                    help="enable gzipfilter mode.", action="store_true")
parser.add_argument("--accesslog", "--accesslog-file",
                    help="location to store access log file.")
parser.add_argument("--errorlog", "--errorlog-file",
                    help="location to store error log file.")
parser.add_argument("--timeout", "--response-timeout", default=6000,
                    help="the number of seconds to allow responses to run.")
parser.add_argument(
    "--environment",
    "--server-environment",
    default="production",
    help="The server.environment entry controls how CherryPy should run.")
getargs = parser.parse_args()

if (getargs.port is not None):
    port = int(getargs.port)
else:
    port = 4123
if (getargs.host is not None):
    host = str(getargs.host)
else:
    host = "127.0.0.1"
if (getargs.timeout is not None):
    timeout = int(getargs.timeout)
else:
    timeout = 6000
if (getargs.accesslog is not None):
    accesslog = str(getargs.accesslog)
else:
    accesslog = "./access.log"
if (getargs.errorlog is not None):
    errorlog = str(getargs.errorlog)
else:
    errorlog = "./errors.log"
if (getargs.environment is not None):
    serv_environ = str(getargs.environment)
else:
    serv_environ = "production"
pro_app_name = "Test Time Server"
pro_app_version = "0.0.1"
pro_app_subname = " " + pro_app_version


class GenerateIndexPage(object):
    def index(self):
        now = datetime.datetime.now()
        utc_now = datetime.datetime.utcnow()
        ts = now.strftime("%s")
        utc_ts = utc_now.strftime("%s")
        ts_str = str(ts)
        utc_ts_str = str(utc_ts)
        ts_ms = now.microsecond
        utc_ts_ms = utc_now.microsecond
        ts_ms_str = str(ts_ms).ljust(6, "0")
        utc_ts_ms_str = str(utc_ts_ms).ljust(6, "0")
        ts_full_str = ts_str + "." + ts_ms_str
        utc_ts_full_str = utc_ts_str + "." + utc_ts_ms_str
        cherrypy.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        cherrypy.response.headers['Datetime-Timestamp'] = utc_ts_str
        cherrypy.response.headers['Datetime-Microseconds'] = utc_ts_ms_str
        cherrypy.response.headers['Datetime-Timestampfull'] = utc_ts_full_str
        return "<!DOCTYPE html>\n<html lang=\"en\">\n    <head>\n        <meta charset=\"utf-8\">\n        <title>" + pro_app_name + pro_app_subname + "</title>\n    </head>\n    <body>\n        <h1>" + pro_app_name + pro_app_subname + "</h1>\n        <h6>\n            Timestamp: " + utc_ts_str + "<br />\n            Microseconds: " + utc_ts_ms_str + \
            "<br />\n            Timestampfull: " + utc_ts_full_str + "<br />\n        </h6>\n        <p>\n            <a href=\"/csv/\">CSV</a>\n            <a href=\"/txt/\">TXT</a>\n            <a href=\"/xml/\">XML</a>\n            <a href=\"/json/\">JSON</a>\n            <a href=\"/text/\">TEXT</a>\n            <a href=\"/yaml/\">YAML</a>\n        </p>\n    </body>\n</html>\n"
    index.exposed = True


class GenerateCSVPage(object):
    def index(self):
        now = datetime.datetime.now()
        utc_now = datetime.datetime.utcnow()
        ts = now.strftime("%s")
        utc_ts = utc_now.strftime("%s")
        ts_str = str(ts)
        utc_ts_str = str(utc_ts)
        ts_ms = now.microsecond
        utc_ts_ms = utc_now.microsecond
        ts_ms_str = str(ts_ms).ljust(6, "0")
        utc_ts_ms_str = str(utc_ts_ms).ljust(6, "0")
        ts_full_str = ts_str + "." + ts_ms_str
        utc_ts_full_str = utc_ts_str + "." + utc_ts_ms_str
        cherrypy.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        cherrypy.response.headers['Datetime-Timestamp'] = utc_ts_str
        cherrypy.response.headers['Datetime-Microseconds'] = utc_ts_ms_str
        cherrypy.response.headers['Datetime-Timestampfull'] = utc_ts_full_str
        return "timestamp,microseconds,timestampfull\n" + utc_ts_str + \
            "," + utc_ts_ms_str + "," + utc_ts_full_str + "\n"
    index.exposed = True


class GenerateTXTPage(object):
    def index(self):
        now = datetime.datetime.now()
        utc_now = datetime.datetime.utcnow()
        ts = now.strftime("%s")
        utc_ts = utc_now.strftime("%s")
        ts_str = str(ts)
        utc_ts_str = str(utc_ts)
        ts_ms = now.microsecond
        utc_ts_ms = utc_now.microsecond
        ts_ms_str = str(ts_ms).ljust(6, "0")
        utc_ts_ms_str = str(utc_ts_ms).ljust(6, "0")
        ts_full_str = ts_str + "." + ts_ms_str
        utc_ts_full_str = utc_ts_str + "." + utc_ts_ms_str
        cherrypy.response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
        cherrypy.response.headers['Datetime-Timestamp'] = utc_ts_str
        cherrypy.response.headers['Datetime-Microseconds'] = utc_ts_ms_str
        cherrypy.response.headers['Datetime-Timestampfull'] = utc_ts_full_str
        return "" + utc_ts_str + "\n" + utc_ts_ms_str + "\n" + utc_ts_full_str + "\n"
    index.exposed = True


class GenerateXMLPage(object):
    def index(self):
        now = datetime.datetime.now()
        utc_now = datetime.datetime.utcnow()
        ts = now.strftime("%s")
        utc_ts = utc_now.strftime("%s")
        ts_str = str(ts)
        utc_ts_str = str(utc_ts)
        ts_ms = now.microsecond
        utc_ts_ms = utc_now.microsecond
        ts_ms_str = str(ts_ms).ljust(6, "0")
        utc_ts_ms_str = str(utc_ts_ms).ljust(6, "0")
        ts_full_str = ts_str + "." + ts_ms_str
        utc_ts_full_str = utc_ts_str + "." + utc_ts_ms_str
        cherrypy.response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
        cherrypy.response.headers['Datetime-Timestamp'] = utc_ts_str
        cherrypy.response.headers['Datetime-Microseconds'] = utc_ts_ms_str
        cherrypy.response.headers['Datetime-Timestampfull'] = utc_ts_full_str
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<datetime>\n <time timestamp=\"" + utc_ts_str + \
            "\" microseconds=\"" + utc_ts_ms_str + "\" timestampfull=\"" + \
            utc_ts_full_str + "\" />\n</datetime>\n"
    index.exposed = True


class GenerateJSONPage(object):
    def index(self):
        now = datetime.datetime.now()
        utc_now = datetime.datetime.utcnow()
        ts = now.strftime("%s")
        utc_ts = utc_now.strftime("%s")
        ts_str = str(ts)
        utc_ts_str = str(utc_ts)
        ts_ms = now.microsecond
        utc_ts_ms = utc_now.microsecond
        ts_ms_str = str(ts_ms).ljust(6, "0")
        utc_ts_ms_str = str(utc_ts_ms).ljust(6, "0")
        ts_full_str = ts_str + "." + ts_ms_str
        utc_ts_full_str = utc_ts_str + "." + utc_ts_ms_str
        cherrypy.response.headers['Content-Type'] = 'text/csv; charset=UTF-8'
        cherrypy.response.headers['Datetime-Timestamp'] = utc_ts_str
        cherrypy.response.headers['Datetime-Microseconds'] = utc_ts_ms_str
        cherrypy.response.headers['Datetime-Timestampfull'] = utc_ts_full_str
        return "{\n  \"datetime\": {\n    \"time\": {\n      \"-timestamp\": \"" + utc_ts_str + "\",\n      \"-microseconds\": \"" + \
            utc_ts_ms_str + "\",\n      \"-timestampfull\": \"" + \
            utc_ts_full_str + "\"\n    }\n  }\n}\n"
    index.exposed = True


class GenerateTEXTPage(object):
    def index(self):
        now = datetime.datetime.now()
        utc_now = datetime.datetime.utcnow()
        ts = now.strftime("%s")
        utc_ts = utc_now.strftime("%s")
        ts_str = str(ts)
        utc_ts_str = str(utc_ts)
        ts_ms = now.microsecond
        utc_ts_ms = utc_now.microsecond
        ts_ms_str = str(ts_ms).ljust(6, "0")
        utc_ts_ms_str = str(utc_ts_ms).ljust(6, "0")
        ts_full_str = ts_str + "." + ts_ms_str
        utc_ts_full_str = utc_ts_str + "." + utc_ts_ms_str
        cherrypy.response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
        cherrypy.response.headers['Datetime-Timestamp'] = utc_ts_str
        cherrypy.response.headers['Datetime-Microseconds'] = utc_ts_ms_str
        cherrypy.response.headers['Datetime-Timestampfull'] = utc_ts_full_str
        return "" + utc_ts_str + "\n" + utc_ts_ms_str + "\n" + utc_ts_full_str + "\n"
    index.exposed = True


class GenerateYAMLPage(object):
    def index(self):
        now = datetime.datetime.now()
        utc_now = datetime.datetime.utcnow()
        ts = now.strftime("%s")
        utc_ts = utc_now.strftime("%s")
        ts_str = str(ts)
        utc_ts_str = str(utc_ts)
        ts_ms = now.microsecond
        utc_ts_ms = utc_now.microsecond
        ts_ms_str = str(ts_ms).ljust(6, "0")
        utc_ts_ms_str = str(utc_ts_ms).ljust(6, "0")
        ts_full_str = ts_str + "." + ts_ms_str
        utc_ts_full_str = utc_ts_str + "." + utc_ts_ms_str
        cherrypy.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        cherrypy.response.headers['Datetime-Timestamp'] = utc_ts_str
        cherrypy.response.headers['Datetime-Microseconds'] = utc_ts_ms_str
        cherrypy.response.headers['Datetime-Timestampfull'] = utc_ts_full_str
        return "---\n  datetime: \n    time: \n      -timestamp: \"" + utc_ts_str + \
            "\"\n      -microseconds: \"" + utc_ts_ms_str + \
            "\"\n      -timestampfull: \"" + utc_ts_full_str + "\"\n"
    index.exposed = True


cherrypy.config.update({"environment": serv_environ,
                        "log.error_file": errorlog,
                        "log.access_file": accesslog,
                        "log.screen": getargs.verbose,
                        "gzipfilter.on": getargs.gzipfilter,
                        "tools.gzip.on": getargs.gzip,
                        "tools.gzip.mime_types": ['text/*'],
                        "server.socket_host": host,
                        "server.socket_port": port,
                        "response.timeout": timeout,
                        })
cherrypy.root = GenerateIndexPage()
cherrypy.root.csv = GenerateCSVPage()
cherrypy.root.txt = GenerateTXTPage()
cherrypy.root.xml = GenerateXMLPage()
cherrypy.root.json = GenerateJSONPage()
cherrypy.root.text = GenerateTEXTPage()
cherrypy.root.yaml = GenerateYAMLPage()
cherrypy.quickstart(cherrypy.root)
