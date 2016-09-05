# -*- coding: utf-8 -*-
# Copyright (c) 2016 Jens Lorrmann


import urllib
import os
import httplib
import re

from xcptions import APIResponseError

HEADER_COOKIE_RE = re.compile(r'__cfduid=([a-f0-9]{46})')
BODY_COOKIE_RE = re.compile(r'document\.cookie="a=([a-f0-9]{32});path=/;";')

class Connection:
    def __init__(self, broker, timeout=30):
        self._timeout = timeout
        self.headers = broker.HEADER
        self._broker = broker
        self.setup_connection( self._broker.DOMAIN )
        

    def setup_connection( self, domain ):
        if ("HTTPS_PROXY" in os.environ):
            match = re.search(r'http://([\w.]+):(\d+)',os.environ['HTTPS_PROXY'])
            if match:
                self.conn = httplib.HTTPSConnection(match.group(1),
                                                port=match.group(2),
                                                timeout=self._timeout)
                self.conn.set_tunnel( domain )
        else:
            self.conn = httplib.HTTPSConnection( domain, timeout=self._timeout )
            
        self.cookie = None
        

    def close(self):
        self.conn.close()
       
       
    def getCookie(self):
        self.cookie = ""

        try:
            self.conn.request("GET", '/')
            response = self.conn.getresponse()
        except Exception:
            # reset connection so it doesn't stay in a weird state if we catch
            # the error in some other place
            self.conn.close()
            self.setup_connection()
            raise

        setCookieHeader = response.getheader("Set-Cookie")
        match = HEADER_COOKIE_RE.search(setCookieHeader)
        if match:
            self.cookie = "__cfduid=" + match.group(1)

        match = BODY_COOKIE_RE.search(response.read())
        if match:
            if self.cookie != "":
                self.cookie += '; '
            self.cookie += "a=" + match.group(1)

   
    def makeRequest(self, url, params={}, extra_headers=None, 
                    with_cookie=False):
                        
                               
        data = urllib.urlencode(params)
        if with_cookie:
            if self.cookie is None:
                self.getCookie()

            self.headers.update({"Cookie": self.cookie})

        # PRIVAT request
        if extra_headers is not None:
            self.headers.update(extra_headers)
            
        try:
            self.conn.request("POST", url, data, self.headers)
            response = self.conn.getresponse()
            
            if response.status < 200 or response.status > 299:
                msg = "API response error: %s".format(response.status)
                
                raise APIResponseError(msg)
            
        except Exception:
            # reset connection so it doesn't stay in a weird state if we catch
            # the error in some other place
            self.conn.close()
            self.setup_connection( self._broker.DOMAIN )
            return self.makeRequest( url, params, extra_headers, with_cookie )
            raise

        return response.read()