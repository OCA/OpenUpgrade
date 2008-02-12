#!/usr/bin/env python

"""
    Authenticating HTTP Server

    This module builds on BaseHTTPServer and implements
    basic authentication

"""

from utils import VERSION, AUTHOR
__version__ = VERSION
__author__  = AUTHOR

import os
import sys
import time
import socket
import string
import posixpath
import SocketServer
import BufferingHTTPServer
import BaseHTTPServer
import base64

from string import atoi,split

AUTH_ERROR_MSG="""<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<HTML><HEAD>
<TITLE>401 Authorization Required</TITLE>
</HEAD><BODY>
<H1>Authorization Required</H1>
This server could not verify that you
are authorized to access the document
requested.  Either you supplied the wrong
credentials (e.g., bad password), or your
browser doesn't understand how to supply
the credentials required.<P>
</BODY></HTML>"""

class AuthRequestHandler:
    """
    Simple handler that use buffering and can check for auth headers

    In order to use it create a subclass of BufferedAuthRequestHandler
    or BasicAuthRequestHandler depending on if you want to send
    responses as block or as stream.

    In your subclass you have to define the method get_userinfo(user,pw)
    which should return 1 or None depending on whether the password was
    ok or not. None means that the user is not authorized.
    """

    # False means no authentiation
    DO_AUTH=1

    AUTH_ERROR_MSG="""<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <HTML><HEAD>
    <TITLE>401 Authorization Required</TITLE>
    </HEAD><BODY>
    <H1>Authorization Required</H1>
    This server could not verify that you
    are authorized to access the document
    requested.  Either you supplied the wrong
    credentials (e.g., bad password), or your
    browser doesn't understand how to supply
    the credentials required.<P>
    </BODY></HTML>"""

    server_version = "AuthHTTP/" + __version__

    def _log(self, message):
        pass

    def handle(self):
        """
        Special handle method with buffering and authentication
        """
        self.infp=os.tmpfile()

        self.infp.write("------------------------------------------------------------------------------\n")
        self.raw_requestline = self.rfile.readline()
        self.infp.write(self.raw_requestline)
        self.request_version = version = "HTTP/0.9" # Default
        requestline = self.raw_requestline

        # needed by send_error
        self.command = requestline
        if requestline[-2:] == '\r\n':
            requestline = requestline[:-2]
        elif requestline[-1:] == '\n':
            requestline = requestline[:-1]

        self.requestline = requestline
        words = string.split(requestline)
        if len(words) == 3:
            [command, path, version] = words
            if version[:5] != 'HTTP/':
                self.send_error(400, "Bad request version (%s)" % `version`)
                return
        elif len(words) == 2:
            [command, path] = words
            if command != 'GET':
                self.send_error(400,
                                "Bad HTTP/0.9 request type (%s)" % `command`)
                return
        else:
            self.send_error(400, "Bad request syntax (%s)" % `requestline`)
            return

        self.command, self.path, self.request_version = command, path, version
        self.headers = self.MessageClass(self.rfile, 0)
        self.infp.write(str(self.headers))
        # test authentification
        global UserName, PassWord
        self.db_name=self.path.split('/')[1]
        UserName, PassWord = 'root',''
        if self.db_name!='':
            if self.DO_AUTH:
                try:
                    a=self.headers["Authorization"]
                    m,up=string.split(a)
                    up2=base64.decodestring(up)
                    user,pw=string.split(up2,":")
                    UserName, PassWord = user,pw
                    if not self.get_userinfo(user,pw):
                        self.send_autherror(401,"Authorization Required"); return
                except Exception ,e:
                    print e
                    self.send_autherror(401,"Authorization Required")
                    return

        # check for methods starting with do_
        mname = 'do_' + command
        if not hasattr(self, mname):
            self.send_error(501, "Unsupported method (%s)" % `command`)
            return

        method = getattr(self, mname)
        method()

        self.infp.flush()
        self.infp.close()
        self._flush()

    def write_infp(self,s):
        self.infp.write(str(s))
        self.infp.flush()

    def send_response(self,code, message=None):
        """Override send_response to use the correct http version
           in the response."""
        self.log_request(code)
        if message is None:
            if self.responses.has_key(code):
                message = self.responses[code][0]
            else:
                message = ''

        if self.request_version != 'HTTP/0.9':
            self._append("%s %s %s\r\n" %
                             (self.request_version, str(code), message))

        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())
        self.send_header('Connection', 'close')

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            self.send_error(403, "Directory listing not supported")
            return None
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None

        self.send_response(200)
        self.send_header("Content-type", self.guess_type(path))
        self.end_headers()
        return f

    def send_autherror(self,code,message=None):
        try:
            short, long = self.responses[code]
        except KeyError:
            short, long = '???', '???'
        if not message:
            message = short
        explain = long

        emsg=self.AUTH_ERROR_MSG
        self.log_error("code %d, message %s", code, message)
        self.send_response(code, message)
        self.send_header("WWW-Authenticate","Basic realm=\"PyWebDAV\"")
        self.send_header("Content-Type", 'text/html')
        self.end_headers()

        lines=split(emsg,"\n")
        for l in lines:
            self._append("%s\r\n" %l)

    def get_userinfo(self,user):
        """ return the password of the user
        Override this class to return the right password
        """

        # Always reject
        return None

class BufferedAuthRequestHandler(BufferingHTTPServer.BufferedHTTPRequestHandler,AuthRequestHandler):

    def handle(self):
        self._init_buffer()
        AuthRequestHandler.handle(self)
        self._flush()

class BasicAuthRequestHandler(BufferingHTTPServer.BufferedHTTPRequestHandler,AuthRequestHandler):

    def _append(self,s):
        """ write the string to wfile """
        self.wfile.write(s)