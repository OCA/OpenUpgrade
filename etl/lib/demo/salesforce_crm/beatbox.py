"""beatbox: Makes the salesforce.com SOAP API easily accessible."""

__version__ = "0.9"
__author__ = "Simon Fell"
__credits__ = "Mad shouts to the sforce possie"
__copyright__ = "(C) 2006 Simon Fell. GNU GPL 2."

import httplib
from urlparse import urlparse
from StringIO import StringIO
import gzip
import datetime
import xmltramp
from xmltramp import islst
from xml.sax.saxutils import XMLGenerator
from xml.sax.saxutils import quoteattr
from xml.sax.xmlreader import AttributesNSImpl

# global constants for namespace strings, used during serialization
_partnerNs = "urn:partner.soap.sforce.com"
_sobjectNs = "urn:sobject.partner.soap.sforce.com"
_envNs = "http://schemas.xmlsoap.org/soap/envelope/"
_noAttrs = AttributesNSImpl({}, {})

# global constants for xmltramp namespaces, used to access response data
_tPartnerNS = xmltramp.Namespace(_partnerNs)
_tSObjectNS = xmltramp.Namespace(_sobjectNs)
_tSoapNS = xmltramp.Namespace(_envNs)

# global config
gzipRequest=True	# are we going to gzip the request ?
gzipResponse=True	# are we going to tell teh server to gzip the response ?
forceHttp=False		# force all connections to be HTTP, for debugging


def makeConnection(scheme, host):
	if forceHttp or scheme.upper() == 'HTTP':
		return httplib.HTTPConnection(host)
	return httplib.HTTPSConnection(host)


# the main sforce client proxy class
class Client:
	def __init__(self):
		self.batchSize = 500
		self.serverUrl = "https://www.salesforce.com/services/Soap/u/7.0"
		self.__conn = None
		
	def __del__(self):
		if self.__conn != None:
			self.__conn.close()
			
	# login, the serverUrl and sessionId are automatically handled, returns the loginResult structure		
	def login(self, username, password):
		lr = LoginRequest(self.serverUrl, username, password).post()
		self.useSession(str(lr[_tPartnerNS.sessionId]), str(lr[_tPartnerNS.serverUrl]))
		return lr

	# initialize from an existing sessionId & serverUrl, useful if we're being launched via a custom link	
	def useSession(self, sessionId, serverUrl):
		self.sessionId = sessionId
		self.__serverUrl = serverUrl
		(scheme, host, path, params, query, frag) = urlparse(self.__serverUrl)
		self.__conn = makeConnection(scheme, host)

	# set the batchSize property on the Client instance to change the batchsize for query/queryMore
	def query(self, soql):
		return QueryRequest(self.__serverUrl, self.sessionId, self.batchSize, soql).post(self.__conn)
	
	def queryMore(self, queryLocator):
		return QueryMoreRequest(self.__serverUrl, self.sessionId, self.batchSize, queryLocator).post(self.__conn)
		
	def getUpdated(self, sObjectType, start, end):
		return GetUpdatedRequest(self.__serverUrl, self.sessionId, sObjectType, start, end).post(self.__conn)
		
	def getDeleted(self, sObjectType, start, end):
		return GetDeletedRequest(self.__serverUrl, self.sessionId, sObjectType, start, end).post(self.__conn)
				
	def retrieve(self, fields, sObjectType, ids):
		return RetrieveRequest(self.__serverUrl, self.sessionId, fields, sObjectType, ids).post(self.__conn)

	# sObjects can be 1 or a list, returns a single save result or a list
	def create(self, sObjects):
		return CreateRequest(self.__serverUrl, self.sessionId, sObjects).post(self.__conn)

	# sObjects can be 1 or a list, returns a single save result or a list
	def update(self, sObjects):
		return UpdateRequest(self.__serverUrl, self.sessionId, sObjects).post(self.__conn)
		
	# sObjects can be 1 or a list, returns a single upsert result or a list
	def upsert(self, externalIdName, sObjects):
		return UpsertRequest(self.__serverUrl, self.sessionId, externalIdName, sObjects).post(self.__conn)	
	
	# ids can be 1 or a list, returns a single delete result or a list
	def delete(self, ids):
		return DeleteRequest(self.__serverUrl, self.sessionId, ids).post(self.__conn)

	# sObjectTypes can be 1 or a list, returns a single describe result or a list of them
	def describeSObjects(self, sObjectTypes):
		return DescribeSObjectsRequest(self.__serverUrl, self.sessionId, sObjectTypes).post(self.__conn)
		
	def describeGlobal(self):
		return AuthenticatedRequest(self.__serverUrl, self.sessionId, "describeGlobal").post(self.__conn)

	def describeLayout(self, sObjectType):
		return DescribeLayoutRequest(self.__serverUrl, self.sessionId, sObjectType).post(self.__conn)
		
	def describeTabs(self):
		return AuthenticatedRequest(self.__serverUrl, self.sessionId, "describeTabs").post(self.__conn, True)

	def getServerTimestamp(self):
		return str(AuthenticatedRequest(self.__serverUrl, self.sessionId, "getServerTimestamp").post(self.__conn)[_tPartnerNS.timestamp])
		
	def resetPassword(self, userId):
		return ResetPasswordRequest(self.__serverUrl, self.sessionId, userId).post(self.__conn)
		
	def setPassword(self, userId, password):
		SetPasswordRequest(self.__serverUrl, self.sessionId, userId, password).post(self.__conn)
		
	def getUserInfo(self):
		return AuthenticatedRequest(self.__serverUrl, self.sessionId, "getUserInfo").post(self.__conn)

	#def convertLead(self, convertLeads):

# fixed version of XmlGenerator, handles unqualified attributes correctly
class BeatBoxXmlGenerator(XMLGenerator):
	def __init__(self, destination, encoding):
		XMLGenerator.__init__(self, destination, encoding)
	
	def makeName(self, name):	
		if name[0] is None:
			#if the name was not namespace-scoped, use the qualified part
			return name[1]
		# else try to restore the original prefix from the namespace
		return self._current_context[name[0]] + ":" + name[1]
		
	def startElementNS(self, name, qname, attrs):
		self._out.write('<' + self.makeName(name))
		
		for pair in self._undeclared_ns_maps:
			self._out.write(' xmlns:%s="%s"' % pair)
		self._undeclared_ns_maps = []
		
		for (name, value) in attrs.items():
			self._out.write(' %s=%s' % (self.makeName(name), quoteattr(value)))
		self._out.write('>')

# general purpose xml writer, does a bunch of useful stuff above & beyond XmlGenerator
class XmlWriter:			
	def __init__(self, doGzip):
		self.__buf = StringIO("")
		if doGzip:
			self.__gzip = gzip.GzipFile(mode='wb', fileobj=self.__buf)
			stm = self.__gzip
		else:
			stm = self.__buf
			self.__gzip = None
		self.xg = BeatBoxXmlGenerator(stm, "utf-8")
		self.xg.startDocument()
		self.__elems = []

	def startPrefixMapping(self, prefix, namespace):
		self.xg.startPrefixMapping(prefix, namespace)
	
	def endPrefixMapping(self, prefix):
		self.xg.endPrefixMapping(prefix)
		
	def startElement(self, namespace, name, attrs = _noAttrs):
		self.xg.startElementNS((namespace, name), name, attrs)
		self.__elems.append((namespace, name))

	# if value is a list, then it writes out repeating elements, one for each value
	def writeStringElement(self, namespace, name, value, attrs = _noAttrs):
		if islst(value):
			for v in value:
				self.writeStringElement(namespace, name, v, attrs)
		else:
			self.startElement(namespace, name, attrs)
			self.characters(value)
			self.endElement()

	def endElement(self):
		e = self.__elems[-1];
		self.xg.endElementNS(e, e[1])
		del self.__elems[-1]

	def characters(self, s):
		# todo base64 ?
		if isinstance(s, datetime.datetime):
			# todo, timezones
			s = s.isoformat()
		elif isinstance(s, datetime.date):
			# todo, try isoformat
			s = "%04d-%02d-%02d" % (s.year, s.month, s.day)
		elif isinstance(s, int):
			s = str(s)
		elif isinstance(s, float):
			s = str(s)
		self.xg.characters(s)

	def endDocument(self):
		self.xg.endDocument()
		if (self.__gzip != None):
			self.__gzip.close();
		return self.__buf.getvalue()

# exception class for soap faults
class SoapFaultError(Exception):
	def __init__(self, faultCode, faultString):
		self.faultCode = faultCode
		self.faultString = faultString
			
	def __str__(self):
		return repr(self.faultCode) + " " + repr(self.faultString)
		
# soap specific stuff ontop of XmlWriter
class SoapWriter(XmlWriter):
	def __init__(self):
		XmlWriter.__init__(self, gzipRequest)
		self.startPrefixMapping("s", _envNs)
		self.startPrefixMapping("p", _partnerNs)
		self.startPrefixMapping("o", _sobjectNs)
		self.startElement(_envNs, "Envelope")
		
	def endDocument(self):
		self.endElement()  # envelope
		self.endPrefixMapping("o")
		self.endPrefixMapping("p")
		self.endPrefixMapping("s")
		return XmlWriter.endDocument(self)	

# processing for a single soap request / response		
class SoapEnvelope:
	def __init__(self, serverUrl, operationName, clientId="BeatBox/" + __version__):
		self.serverUrl = serverUrl
		self.operationName = operationName
		self.clientId = clientId

	def writeHeaders(self, writer):
		pass

	def writeBody(self, writer):
		pass

	def makeEnvelope(self):
		s = SoapWriter()
		s.startElement(_envNs, "Header")
		s.characters("\n")
		s.startElement(_partnerNs, "CallOptions")
		s.writeStringElement(_partnerNs, "client", self.clientId)
		s.endElement()
		s.characters("\n")
		self.writeHeaders(s)
		s.endElement()	# Header
		s.startElement(_envNs, "Body")
		s.characters("\n")
		s.startElement(_partnerNs, self.operationName)
		self.writeBody(s)
		s.endElement()	# operation
		s.endElement()  # body
		return s.endDocument()

	# does all the grunt work, 
	#   serializes the request, 
	#   makes a http request, 
	#   passes the response to tramp
	#   checks for soap fault
	#   todo: check for mU='1' headers
	#   returns the relevant result from the body child
	def post(self, conn=None, alwaysReturnList=False):
		headers = { "User-Agent": "BeatBox/" + __version__,
					"SOAPAction": "\"\"",
					"Content-Type": "text/xml; charset=utf-8" }
		if gzipResponse:
			headers['accept-encoding'] = 'gzip'
		if gzipRequest:
			headers['content-encoding'] = 'gzip'					
		close = False
		(scheme, host, path, params, query, frag) = urlparse(self.serverUrl)
		if conn == None:
			conn = makeConnection(scheme, host)
			close = True
		conn.request("POST", path, self.makeEnvelope(), headers)
		response = conn.getresponse()
		rawResponse = response.read()
		if response.getheader('content-encoding','') == 'gzip':
			rawResponse = gzip.GzipFile(fileobj=StringIO(rawResponse)).read()
		if close:
			conn.close()
		tramp = xmltramp.parse(rawResponse)
		try:
			faultString = str(tramp[_tSoapNS.Body][_tSoapNS.Fault].faultstring)
			faultCode   = str(tramp[_tSoapNS.Body][_tSoapNS.Fault].faultcode).split(':')[-1]
			raise SoapFaultError(faultCode, faultString)
		except KeyError:
			pass
		# first child of body is XXXXResponse
		result = tramp[_tSoapNS.Body][0]
		# it contains either a single child, or for a batch call multiple children
		if alwaysReturnList or len(result) > 1:
			return result[:]
		else:
			return result[0]
	

class LoginRequest(SoapEnvelope):
	def __init__(self, serverUrl, username, password):
		SoapEnvelope.__init__(self, serverUrl, "login")
		self.__username = username
		self.__password = password

	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "username", self.__username)
		s.writeStringElement(_partnerNs, "password", self.__password)


# base class for all methods that require a sessionId
class AuthenticatedRequest(SoapEnvelope):
	def __init__(self, serverUrl, sessionId, operationName):
		SoapEnvelope.__init__(self, serverUrl, operationName)
		self.sessionId = sessionId

	def writeHeaders(self, s):
		s.startElement(_partnerNs, "SessionHeader")
		s.writeStringElement(_partnerNs, "sessionId", self.sessionId)
		s.endElement()

	def writeSObjects(self, s, sObjects, elemName="sObjects"):
		if islst(sObjects):
			for o in sObjects:
				self.writeSObjects(s, o, elemName)
		else:
			s.startElement(_partnerNs, elemName)
			# type has to go first
			s.writeStringElement(_sobjectNs, "type", sObjects['type'])
			for fn in sObjects.keys():
				if (fn != 'type'):
					s.writeStringElement(_sobjectNs, fn, sObjects[fn])
			s.endElement()
		
						
class QueryOptionsRequest(AuthenticatedRequest):
	def __init__(self, serverUrl, sessionId, batchSize, operationName):
		AuthenticatedRequest.__init__(self, serverUrl, sessionId, operationName)
		self.batchSize = batchSize
		
	def writeHeaders(self, s):
		AuthenticatedRequest.writeHeaders(self, s)
		s.startElement(_partnerNs, "QueryOptions")
		s.writeStringElement(_partnerNs, "batchSize", self.batchSize)
		s.endElement()
		
		
class QueryRequest(QueryOptionsRequest):
	def __init__(self, serverUrl, sessionId, batchSize, soql):
		QueryOptionsRequest.__init__(self, serverUrl, sessionId, batchSize, "query")
		self.__query = soql
				
	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "queryString", self.__query)


class QueryMoreRequest(QueryOptionsRequest):
	def __init__(self, serverUrl, sessionId, batchSize, queryLocator):
		QueryOptionsRequest.__init__(self, serverUrl, sessionId, batchSize, "queryMore")
		self.__queryLocator = queryLocator
		
	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "queryLocator", self.__queryLocator)
		

class GetUpdatedRequest(AuthenticatedRequest):
	def __init__(self, serverUrl, sessionId, sObjectType, start, end, operationName="getUpdated"):
		AuthenticatedRequest.__init__(self, serverUrl, sessionId, operationName)
		self.__sObjectType = sObjectType
		self.__start = start;
		self.__end = end;
		
	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "sObjectType", self.__sObjectType)
		s.writeStringElement(_partnerNs, "startDate", self.__start)
		s.writeStringElement(_partnerNs, "endDate", self.__end)						
			

class GetDeletedRequest(GetUpdatedRequest):
	def __init__(self, serverUrl, sessionId, sObjectType, start, end):
		GetUpdatedRequest.__init__(self, serverUrl, sessionId, sObjectType, start, end, "getDeleted")

	
class UpsertRequest(AuthenticatedRequest):
	def __init__(self, serverUrl, sessionId, externalIdName, sObjects):
		AuthenticatedRequest.__init__(self, serverUrl, sessionId, "upsert")
		self.__externalIdName = externalIdName
		self.__sObjects = sObjects
		
	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "externalIDFieldName", self.__externalIdName)
		self.writeSObjects(s, self.__sObjects)


class UpdateRequest(AuthenticatedRequest):
	def __init__(self, serverUrl, sessionId, sObjects, operationName="update"):
		AuthenticatedRequest.__init__(self, serverUrl, sessionId, operationName)
		self.__sObjects = sObjects
		
	def writeBody(self, s):
		self.writeSObjects(s, self.__sObjects)
				

class CreateRequest(UpdateRequest):		
	def __init__(self, serverUrl, sessionId, sObjects):
		UpdateRequest.__init__(self, serverUrl, sessionId, sObjects, "create")
		

class DeleteRequest(AuthenticatedRequest):
	def __init__(self, serverUrl, sessionId, ids):
		AuthenticatedRequest.__init__(self, serverUrl, sessionId, "delete")
		self.__ids = ids;
		
	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "id", self.__ids)
				
		
class RetrieveRequest(AuthenticatedRequest):
	def __init__(self, serverUrl, sessionId, fields, sObjectType, ids):
		AuthenticatedRequest.__init__(self, serverUrl, sessionId, "retrieve")
		self.__fields = fields
		self.__sObjectType = sObjectType
		self.__ids = ids
		
	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "fieldList", self.__fields)
		s.writeStringElement(_partnerNs, "sObjectType", self.__sObjectType);
		s.writeStringElement(_partnerNs, "ids", self.__ids)
			
		
class ResetPasswordRequest(AuthenticatedRequest):
	def __init__(self, serverUrl, sessionId, userId):
		AuthenticatedRequest.__init__(self, serverUrl, sessionId, "resetPassword")
		self.__userId = userId
		
	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "userId", self.__userId)
		

class SetPasswordRequest(AuthenticatedRequest):
	def __init__(self, serverUrl, sessionId, userId, password):
		AuthenticatedRequest.__init__(self, serverUrl, sessionId, "setPassword")
		self.__userId = userId
		self.__password = password
		
	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "userId", self.__userId)
		s.writeStringElement(_partnerNs, "password", self.__password)	
		
				
class DescribeSObjectsRequest(AuthenticatedRequest):
	def __init__(self, serverUrl, sessionId, sObjectTypes):
		AuthenticatedRequest.__init__(self, serverUrl, sessionId, "describeSObjects")
		self.__sObjectTypes = sObjectTypes
	
	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "sObjectType", self.__sObjectTypes)
			
		
class DescribeLayoutRequest(AuthenticatedRequest):
	def __init__(self, serverUrl, sessionId, sObjectType):
		AuthenticatedRequest.__init__(self, serverUrl, sessionId, "describeLayout")
		self.__sObjectType = sObjectType
		
	def writeBody(self, s):
		s.writeStringElement(_partnerNs, "sObjectType", self.__sObjectType)
