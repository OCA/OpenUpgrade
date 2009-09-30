#!/usr/bin/python

"""soql2atom: a beatbox demo that generates an atom 1.0 formatted feed of any SOQL query (requires beatbox 0.9 or later)

   The fields Id, SystemModStamp and CreatedDate are automatically added to the SOQL if needed.
   The first field in the select list becomes the title of the entry, so make sure to setup the order of the fields as you need.
   The soql should be passed via a 'soql' queryString parameter
   Optionally, you can also pass a 'title' queryString parameter to set the title of the feed

   The script forces authentication, but many apache installations are configured to block the AUTHORIZATION header,
   so the scirpt looks for X_HTTP_AUTHORIZATION instead, you can use a mod_rewrite rule to manage the mapping, something like this

   Options +FollowSymLinks
   RewriteEngine on
   RewriteRule ^(.*)$ soql2atom.py [E=X-HTTP_AUTHORIZATION:%{HTTP:Authorization},QSA,L]

   I have this in a .htaccess file in the same directory as soql2atom.py etc.
"""

__version__ = "1.0"
__author__ = "Simon Fell"
__copyright__ = "(C) 2006 Simon Fell. GNU GPL 2."

import sys
import beatbox
import cgi
import cgitb
from xml.sax.xmlreader import AttributesNSImpl
import datetime
from urlparse import urlparse
import os 
import base64
import string

cgitb.enable()
sf = beatbox._tPartnerNS
svc = beatbox.Client()
_noAttrs = beatbox._noAttrs

def addRequiredFieldsToSoql(soql):
	findPos = string.find(string.lower(soql), "from")
	selectList = []
	for f in string.lower(soql)[:findPos].split(","):
		selectList.append(string.strip(f))
	if not "id" in selectList: selectList.append("Id")
	if not "systemmodstamp" in selectList: selectList.append("systemModStamp")
	if not "createddate" in selectList: selectList.append("createdDate")
	return string.join(selectList, ", ") + soql[findPos-1:]
			
def soql2atom(loginResult, soql, title):
	soqlWithFields = addRequiredFieldsToSoql(soql)
	userInfo = loginResult[beatbox._tPartnerNS.userInfo]
	serverUrl = str(loginResult[beatbox._tPartnerNS.serverUrl])
	(scheme, host, path, params, query, frag) = urlparse(serverUrl)
	sfbaseUrl = scheme + "://" + host + "/"
	thisUrl = "http://" + os.environ["HTTP_HOST"] + os.environ["REQUEST_URI"]
	qr = svc.query(soqlWithFields)
	
	atom_ns = "http://www.w3.org/2005/Atom"
	ent_ns = "urn:sobject.enterprise.soap.sforce.com"

	print "content-type: application/atom+xml"
	doGzip = os.environ.has_key("HTTP_ACCEPT_ENCODING") and "gzip" in string.lower(os.environ["HTTP_ACCEPT_ENCODING"]).split(',')
	if (doGzip): print "content-encoding: gzip"
	print ""
	x = beatbox.XmlWriter(doGzip)
	x.startPrefixMapping("a", atom_ns)
	x.startPrefixMapping("s", ent_ns)
	x.startElement(atom_ns, "feed")
	x.writeStringElement(atom_ns, "title", title)
	x.characters("\n")
	x.startElement(atom_ns, "author")
	x.writeStringElement(atom_ns, "name", str(userInfo.userFullName))
	x.endElement()
	x.characters("\n")
	rel = AttributesNSImpl( {(None, "rel"): "self", (None, "href") : thisUrl}, 
						    {(None, "rel"): "rel",  (None, "href"): "href"})
	x.startElement(atom_ns, "link", rel)
	x.endElement()
	x.writeStringElement(atom_ns, "updated", datetime.datetime.utcnow().isoformat() +"Z") 
	x.writeStringElement(atom_ns, "id", thisUrl + "&userid=" + str(loginResult[beatbox._tPartnerNS.userId]))
	x.characters("\n")
	type = AttributesNSImpl({(None, u"type") : "html"}, {(None, u"type") : u"type" })
	for row in qr[sf.records:]:
		x.startElement(atom_ns, "entry")
		desc = ""
		x.writeStringElement(atom_ns, "title", str(row[2]))
		for col in row[2:]:
			if col._name[1] == 'Id':
				x.writeStringElement(atom_ns, "id", sfbaseUrl + str(col))
				writeLink(x, atom_ns, "link", "alternate", "text/html", sfbaseUrl + str(col))
			elif col._name[1] == 'SystemModstamp':
				x.writeStringElement(atom_ns, "updated", str(col))
			elif col._name[1] == 'CreatedDate':
				x.writeStringElement(atom_ns, "published", str(col))
			elif str(col) != "":
				desc = desc + "<b>" + col._name[1] + "</b> : " + str(col) + "<br>"
				x.writeStringElement(ent_ns, col._name[1], str(col))
		x.startElement(atom_ns, "content", type)
		x.characters(desc)
		x.endElement() # content
		x.characters("\n")
		x.endElement() # entry
	x.endElement() # feed
	print x.endDocument()

def writeLink(x, namespace, localname, rel, type, href):
	rel = AttributesNSImpl( {(None, "rel"): rel,   (None, "href"): href,   (None, "type"): type }, 
						    {(None, "rel"): "rel", (None, "href"): "href", (None, "type"): "type"})
	x.startElement(namespace, localname, rel)
	x.endElement()

def authenticationRequired(message="Unauthorized"):
	print "status: 401 Unauthorized"
	print "WWW-authenticate: Basic realm=""www.salesforce.com"""
	print "content-type: text/plain"
	print ""
	print message

if not os.environ.has_key('X_HTTP_AUTHORIZATION') or os.environ['X_HTTP_AUTHORIZATION'] == '':
	authenticationRequired()
else:
	auth = os.environ['X_HTTP_AUTHORIZATION']
	(username, password) = base64.decodestring(auth.split(" ")[1]).split(':')
	form = cgi.FieldStorage()
	if not form.has_key('soql'): raise Exception("Must provide the SOQL query to run via the soql queryString parameter")
	soql = form.getvalue("soql")
	title = "SOQL2ATOM : " + soql
	if form.has_key("title"):
		title = form.getvalue("title")
	try:
		lr = svc.login(username, password)	
		soql2atom(lr, soql, title)
	except beatbox.SoapFaultError, sfe:
		if (sfe.faultCode == 'INVALID_LOGIN'):
			authenticationRequired(sfe.faultString)
		else:
			raise
			