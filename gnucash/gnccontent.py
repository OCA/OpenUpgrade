#**********************************************************************
#   Copyright (c) 2009 P. Christeas <p_christ@hol.gr>
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with this library; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#   See:  http://www.gnu.org/licenses/lgpl.html
#

#---------------------------
# Code taken from Knut Gerwens
#   gnuc2ooo@alice-dsl.net

import xml.sax as sax
#import os.path, locale
import time

class GCDbgHandler (object):
	"""This class implements a dummy output of the parsed data to
	the screen (stdout).
	Override the class and add your backend support"""
	def __init__(self):
		self.linesout=0
		self.printed = {'account': 5, 'trans' :5, 'commodity': 2, 'invoice' :2, 'entry': 2}
		self.counters = {}
	def debug(self,stri):
		if self.linesout > 200:
			return
		self.dprint(stri)
		self.linesout+=1
	def warn(self,stri):
		self.dprint(stri)
	def decCount(self,cnt):
		if self.counters.has_key(cnt):
			self.counters[cnt]-=1
		else:
			self.counters[cnt]=-1
	def go_quiet(self):
		for key in self.printed.keys():
			self.printed[key] = 0
	def dprint(self,*args):
		st=map(lambda a: str(a),args)
		print(' '.join(st))
		
	def print_item(self,name,item):
		if not self.printed.has_key(name):
			self.dprint("I won't print %s" % name)
			self.printed[name] = 0
			return
		if self.printed[name] > 0 :
			self.dprint("Item %s:" % name, item.__dict__)
			self.printed[name] -= 1
	
	def fill_idref(self,idv,obj):
		pass
	
	def start_book(self,book):
		self.debug("Start Gnucash book")
		
	def set_book(self,book):
		self.debug("Set Gnucash book")

	def end_book(self,book):
		self.decCount('book')
		self.debug("End Gnucash book")
		dd = {}
		for key,val in self.counters.iteritems():
			if val:
				dd[str(key)] = val
		self.dprint('Counters left:',dd)

	def end_account(self,act,par):
		self.decCount('account')
		self.print_item('account',act)

	def end_transaction(self,trn,par):
		self.decCount('transaction')
		self.print_item('trans',trn)
		
	def setCounter(self,ctype,count):
		self.counters[ctype]=count
	
	def get_commodity(self,book,com):
		self.decCount('commodity')
		self.print_item('commodity',com)
	
	def end_vendor(self,act,par):
		self.decCount('gnc:GncVendor')
		self.print_item('vendor',act)
		
	def find_commodity(self,dic):
		return False

	def end_customer(self,act,par):
		self.decCount('gnc:GncCustomer')
		self.print_item('customer',act)

	def end_invoice(self,act,par):
		self.decCount('gnc:GncInvoice')
		self.print_item('invoice',act)

	def end_entry(self,act,par):
		self.decCount('gnc:GncEntry')
		self.print_item('entry',act)


class gnc_elem(object):
	def __init__(self,name =''):
		self.name =name
	def create(self,oh,name):
		return gnc_elem(name)
	def begin(self,oh,attrs):
		pass
	def end(self,oh,parent):
		pass
	def getchars(self,oh,chars):
		pass
	def get_slots(self,slots):
		print( 'Got slots in %s'% self.name,slots)
	
gnc_unk_instances = {}
class gnc_unk_elem(gnc_elem):
	def __init__(self,name ='',pname=''):
		self.name =name
		self.pname=pname
	def begin(self,oh,attrs):
		global gnc_unk_instances
		if not self.pname:
			return
		if gnc_unk_instances.has_key(self.pname):
			if self.name in gnc_unk_instances[self.pname]:
				return
			gnc_unk_instances[self.pname].append(self.name)
			oh.warn("Unknown elem: %s in %s"%(self.name, self.pname))
		else:
			gnc_unk_instances[self.pname]=[self.name,]
			oh.warn("Unknown elem: %s in %s"%(self.name, self.pname))

class gnc_elem_dict(gnc_elem):
	def __init__(self,name):
		self.name = name
		self.dic = {}
	def setDict(self,oh,key,val):
		self.dic[key]=val
	def setID(self,oh,val):
		self.dic['id']=val

class gnc_v2_elem(gnc_elem):
	def create(self,oh,name):
		if name == "gnc:book":
			return gnc_book_elem(name)
		elif name == "gnc:count-data":
			return gnc_count_elem(name)
		return gnc_unk_elem(name,self.name)
	def begin(self,oh,attrs):
		oh.debug("Start Gnucash elem")
		pass
	def end(self,oh,parent):
		oh.debug("End Gnucash elem")
		pass

class gnc_count_elem(gnc_elem):
	def __init__(self,name =''):
		self.name =name
		self.ctype='other'
		self.count=0
	def create(self,oh,name):
		return gnc_unk_elem(name,self.name)
	def begin(self,oh,attrs):
		self.ctype=attrs.get('cd:type','other')
		#oh.debug("Count elem for %s"%self.ctype)
		pass
	def end(self,oh,parent):
		oh.setCounter(self.ctype,self.count)
		#oh.debug("End count elem: %d %ss"%(self.count,self.ctype))
		pass
	def getchars(self,oh,chars):
		self.count=int(chars)

class gnc_book_elem(gnc_elem):
	def __init__(self,name):
		super(gnc_book_elem,self).__init__(name)
		self.bookid = None
		self.commodity = None
	def create(self,oh,name):
		if name == "gnc:account":
			return gnc_account_elem(name)
		if name == "gnc:transaction":
			return gnc_trns_elem(name)
		elif name == "gnc:count-data":
			return gnc_count_elem(name)
		elif name == 'book:slots':
			return gnc_elem_slots(name)
		elif name == 'book:id':
			return gnc_elem_var_id(name)
		elif name == 'gnc:commodity':
			return gnc_elem_commodity(name)
		elif name == 'gnc:GncVendor':
			return gnc_elem_vendor(name)
		elif name == 'gnc:GncCustomer':
			return gnc_elem_customer(name)
		elif name == 'gnc:GncInvoice':
			return gnc_elem_invoice(name)
		elif name == 'gnc:GncEntry':
			return gnc_elem_entry(name)
		return gnc_unk_elem(name,self.name)

	def begin(self,oh,attrs):
		oh.start_book(self)

	def end(self,oh,parent):
		oh.end_book(self)
	
	def setID(self,oh,val):
		self.bookid=val
		oh.set_book(self)
	def get_commodity(self,oh,com):
		oh.get_commodity(self,com)

class gnc_account_elem(gnc_elem_dict):
	def __init__(self,name=''):
		super(gnc_account_elem,self).__init__(name)
		self.slots =[]
		self.commodity=None
	def create(self,oh,name):
		if name == "act:name" or name =="act:type" or name == 'act:code' or name =='act:description':
			return gnc_elem_var(name)
		if name == "act:id":
			return gnc_elem_var_id(name)
		if name == 'act:parent':
			return gnc_elem_var_ref(name)
		if name == "act:commodity-scu":
			return gnc_elem(name)
		if name == "act:commodity":
			return gnc_elem_commodity(name)
		if name == "act:slots":
			return gnc_elem_slots(name)
		return gnc_unk_elem(name,self.name)
	def begin(self,oh,attrs):
		#oh.debug("Start Gnucash account")
		pass
	def end(self,oh,parent):
		oh.end_account(self,parent)
	def get_slots(self,slots):
		self.slots.extend(slots)
	def get_commodity(self,oh,com):
		self.commodity=com.dic

class gnc_elem_var(gnc_elem):
	def __init__(self,name =''):
		self.name =name
		self.val=''
	def create(self,oh,name):
		#if name == "gnc:sst":
		#	return gnc_account_elem(name)
		return gnc_unk_elem(name,self.name)
	#def begin(self,oh,attrs):
	#	pass
	def end(self,oh,parent):
		parent.setDict(oh,self.name.split(':')[1],self.val)
	
	def getchars(self,oh,chars):
		self.val+=chars

class gnc_elem_var_ren(gnc_elem_var):
	def __init__(self,name,rename):
		self.name =name
		self.rename= rename
		self.val=''
	def end(self,oh,parent):
		parent.setDict(oh,self.rename,self.val)
	
class gnc_elem_var_qty(gnc_elem_var):
	#def begin(self,oh,attrs):
	#	pass
	def end(self,oh,parent):
		self.getval(self.val)
		parent.setDict(oh,self.name.split(':')[1],self.val)
	
	def getval(self,chars):
		l_split = chars.strip().split('/')
		if len(l_split) == 1:
			self.val = float(l_split[0])
			return
		elif len(l_split) != 2:
			raise Exception('not a fraction in qty (%s)'%chars)
		if (not l_split[1].isdigit):
			raise Exception('Invalid fraction: %s'%chars)
		if float(l_split[1])== 0.0:
			raise Exception('Divide by zero in qty')
		self.val = float(l_split[0]) / float(l_split[1])

class gnc_elem_var2(gnc_elem_var):
	"""A variable that could also take type="frame" with sub-elements
	"""
	def __init__(self,name =''):
		super(gnc_elem_var2,self).__init__(name)
		self.vtype=''
		self.is_frame= False
		self.slots=[]
	def begin(self,oh,attrs):
		if attrs.has_key('type'):
			self.vtype=attrs.get('type')
			self.is_frame= (self.vtype =='frame')
		if self.is_frame:
			self.val = {}
	
	def create(self,oh,name):
		if name == 'slot':
			if not self.is_frame:
				raise Exception("slot came in a non-frame var")
			return gnc_elem_slot(name)
		return gnc_unk_elem(name,self.name)
	def getchars(self,oh,chars):
		if self.is_frame:
			raise Exception("Loose characters in a frame. \"%s\""%chars)
		else:
			return super(gnc_elem_var2,self).getchars(oh,chars)
	def end(self,oh,parent):
		if (self.is_frame):
			self.val=dict(self.slots)
		return super(gnc_elem_var2,self).end(oh,parent)
	
	
class gnc_elem_commodity(gnc_elem_dict):
	def create(self,oh,name):
		if ':' in name:
			(tbl,key)=name.split(':')
			if tbl == 'cmdty' and (key in [ 'id', 'name', 'space','fraction',
				'get_quotes','quote_tz','quote_source']):
				#id is a normal string, too.
				return gnc_elem_var(name)
		return gnc_unk_elem(name,self.name)
	def end(self,oh,parent):
		self.dic['ref']= oh.find_commodity(self.dic)
		parent.get_commodity(oh,self)

class gnc_elem_slots(gnc_elem):
	def __init__(self,name):
		self.name = name
		self.slots=[]
	def create(self,oh,name):
		if name == 'slot':
			return gnc_elem_slot(name)
		return gnc_unk_elem(name,self.name)
	def end(self,oh,parent):
		parent.get_slots(self.slots)

class gnc_elem_slot(gnc_elem):
	def __init__(self,name):
		self.name = name
		self.key=None
		self.value=None
	def create(self,oh,name):
		if name in ['slot:key','slot:value']:
			return gnc_elem_var2(name)
		return gnc_unk_elem(name,self.name)
	def setDict(self,oh,key,val):
		if key == 'key':
			self.key=val
		elif key == 'value':
			self.value=val
		else:
			raise Exception("incorrect dict in slot")
	def end(self,oh,parent):
		parent.slots.append((self.key,self.value))

class gnc_trns_elem(gnc_elem_dict):
	def __init__(self,name=''):
		super(gnc_trns_elem,self).__init__(name)
		self.splits=[]
		self.commodity=None
	def create(self,oh,name):
		if ':' in name:
			(tbl,key) = name.split(':')
			if tbl == 'trn':
				if key == 'id':
					return gnc_elem_var_id(name)
				elif key == 'description':
					return gnc_elem_var(name)
				elif key == 'num':
					return gnc_elem_var(name)
				elif key == 'currency':
					return gnc_elem_commodity(name)
				elif key in [ 'date-posted', 'date-entered']:
					return gnc_elem_date(name)
				elif key == 'splits':
					return gnc_elem_trn_splits(name)
				elif key == 'slots':
					return gnc_elem_slots(name)
		return gnc_unk_elem(name,self.name)
			
	def end(self,oh,parent):
		oh.end_transaction(self,parent)
	def get_slots(self,slots):
		for slot in slots:
			if slot[0] in ['notes','trans-txn-type','gncInvoice',
				'trans-read-only', 'trans-date-due']:
				self.dic[slot[0]]=slot[1]
			else:
				print 'Got unknown slot %s in %s'%(slot[0],self.name)

	def get_commodity(self,oh,com):
		self.commodity=com.dic

from datetime import datetime
class gnc_elem_date(gnc_elem):
	def __init__(self,name):
		self.name = name
		self.value=None
		self.ns = None
	def parse_date(self,val):
		tzval='+0000'
		if len(val)>19:
			tzval=val[20:]
			val=val[:19].strip()
		date= None
		for fmt in [ '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d%H:%M:%S' ] :
			try:
				date=datetime.strptime(val,fmt)
			except ValueError,er:
				continue
			break
		#print "TZ: ", tzval
		if not date:
			raise ValueError("Cannot parse date: %s"%val)
		return date;
			
	def create(self,oh,name):
		if name == 'ts:date' or name == 'ts:ns':
			return gnc_elem_var(name)
		return gnc_unk_elem(name,self.name)
	def setDict(self,oh,key,val):
		if key == 'date':
		    self.value=self.parse_date(val)
		elif key == 'ns':
			self.ns=val
	def end(self,oh,parent):
		parent.setDict(oh,self.name.split(':')[1],self.value)
		#what to do with self.ns?

class gnc_elem_trn_splits(gnc_elem_dict):
	def __init__(self,name=''):
		super(gnc_elem_trn_splits,self).__init__(name)
		self.splits=[]
	def create(self,oh,name):
		if name == 'trn:split':
			return gnc_elem_trn_split(name)
		return gnc_unk_elem(name,self.name)
	def end(self,oh,parent):
		parent.splits.extend(self.splits)

class gnc_elem_trn_split(gnc_elem_dict):
	def create(self,oh,name):
		if ':' in name:
			(tbl,key)=name.split(':')
			if tbl != 'split':
				return gnc_unk_elem(name,self.name)
			if key == 'id':
				return gnc_elem_var_id(name)
			if key == 'account':
				return gnc_elem_var_ref(name)
			elif key in ['value','quantity']:
				return gnc_elem_var_qty(name)
			elif key == 'reconcile-date':
				return gnc_elem_date(name)
			elif key in [ 'memo','action']:
				return gnc_elem_var(name)
			elif key in [ 'reconciled-state']:
				return gnc_elem_var(name)
		return gnc_unk_elem(name,self.name)
	def end(self,oh,parent):
		parent.splits.append(self.dic)

class gnc_elem_partner(gnc_elem_dict):
	def getns(self):
		return 'not this'
	def create(self,oh,name):
		if ':' in name:
			(tbl,key)=name.split(':')
			if tbl != self.getns():
				return gnc_unk_elem(name,self.name)
			if key == 'guid':
				return gnc_elem_var_id(name)
			#elif key in ['value','quantity']:
			#	return gnc_elem_var_qty(name)
			#elif key == 'reconcile-date':
			#	return gnc_elem_date(name)
			elif key == 'id' :
				return gnc_elem_var_ren(name,'partner_ref')
			elif key in [ 'name','use-tt']:
				return gnc_elem_var(name)
			elif key in [ 'active']:
				return gnc_elem_var(name)
			elif key in [ 'currency']:
				return gnc_elem_commodity(name)
			elif key in [ 'addr' ]:
				return gnc_elem_address(name)
		return gnc_unk_elem(name,self.name)
	def get_commodity(self,oh,com):
		self.dic['commodity']=com.dic

class gnc_elem_vendor(gnc_elem_partner):
	def getns(self):
		return 'vendor'
	def end(self,oh,parent):
		oh.end_vendor(self,parent)
		#parent.splits.append(self.dic)

class gnc_elem_customer(gnc_elem_partner):
	def getns(self):
		return 'cust'
	def end(self,oh,parent):
		oh.end_customer(self,parent)
		#parent.splits.append(self.dic)

class gnc_elem_address(gnc_elem_dict):
	def create(self,oh,name):
		if ':' in name:
			(tbl,key)=name.split(':')
			if tbl == 'addr' and (key in [ 'name', 'addr1','addr2', 'addr3', 'addr4', 'phone', 'email' ]):
				#id is a normal string, too.
				return gnc_elem_var(name)
		return gnc_unk_elem(name,self.name)
	def end(self,oh,parent):
		#parent.get_address(oh,self) *-*
		pass

class gnc_elem_invoice(gnc_elem_dict):
	def __init__(self,name=''):
		super(gnc_elem_invoice,self).__init__(name)
		self.slots =[]
		self.commodity=None
	def create(self,oh,name):
		(tbl, key) = name.split(':')
		if tbl != 'invoice':
			return gnc_unk_elem(name,self.name)
		
		if key in [ 'active', 'billing_id', 'notes' ]:
			return gnc_elem_var(name)
		elif key == "guid":
			return gnc_elem_var_id(name)
		elif key == "id":
			return gnc_elem_var_ren(name,'inv_ref')
		elif key in [ 'posttxn', 'postlot', 'postacc', 'terms' ]:
			return gnc_elem_var_ref(name)
		elif key in [ 'owner', 'billto' ]:
			return gnc_elem_var_ref2(name)
		elif key == "currency":
			return gnc_elem_commodity(name)
		elif key in [ 'posted', 'opened']:
			return gnc_elem_date(name)
		elif key == "slots":
			return gnc_elem_slots(name)
		return gnc_unk_elem(name,self.name)
	def begin(self,oh,attrs):
		#oh.debug("Start Gnucash account")
		pass
	def end(self,oh,parent):
		oh.end_invoice(self,parent)
		pass
	def get_slots(self,slots):
		self.slots.extend(slots)
	def get_commodity(self,oh,com):
		self.dic['currency']=com.dic

class gnc_elem_entry(gnc_elem_dict):
	def __init__(self,name=''):
		super(gnc_elem_entry,self).__init__(name)
		self.slots =[]
		#self.commodity=None
	def create(self,oh,name):
		(tbl, key) = name.split(':')
		if tbl != 'entry':
			return gnc_unk_elem(name,self.name)
		
		if key == "guid":
			return gnc_elem_var_id(name)
		elif key in [ 'description', 'i-taxable', 'i-taxincluded', 
			'i-disc-type', 'i-disc-how', 'action', 'billable', 
			'b-taxable', 'b-taxincluded', 'b-pay' ]:
			return gnc_elem_var(name)
		elif key in [ 'invoice', 'i-acct', 'i-taxtable', 'b-acct', 
			'bill', 'b-taxtable' ]:
			return gnc_elem_var_ref(name)
		elif key in ['qty', 'i-price', 'b-price', 'i-discount' ]:
			return gnc_elem_var_qty(name)
		elif key in [ 'date', 'entered']:
			return gnc_elem_date(name)
		elif key == "slots":
			return gnc_elem_slots(name)
		return gnc_unk_elem(name,self.name)
	def begin(self,oh,attrs):
		#oh.debug("Start Gnucash account")
		pass
	def end(self,oh,parent):
		oh.end_entry(self,parent)
		pass
	def get_slots(self,slots):
		self.slots.extend(slots)
	#def get_commodity(self,oh,com):
	#	self.commodity=com.dic

class gnc_elem_var_id(gnc_elem_var):
	""" The declaration of the id for some object """
	def __init__(self,name =''):
		super(gnc_elem_var_id,self).__init__(name)
	def begin(self,oh,attrs):
		if attrs.get('type') != 'guid':
			oh.debug("ID is not a guid! '%s'"%str(attrs.get('type')))
		super(gnc_elem_var_id,self).begin(oh,attrs)
	def end(self,oh,parent):
		parent.setID(oh,self.val)

class gnc_elem_var_ref(gnc_elem_var):
	""" Reference to object, by id """
	def __init__(self,name =''):
		super(gnc_elem_var_ref,self).__init__(name)
		self.ref=None
	def begin(self,oh,attrs):
		if attrs.get('type') != 'guid':
			oh.warn("Reference ID is not a guid! '%s'"%str(attrs.get('type')))
		super(gnc_elem_var_ref,self).begin(oh,attrs)
	def end(self,oh,parent):
		oh.fill_idref(self,parent)
		parent.setDict(oh,self.name.split(':')[1],(self.val,self.ref))

class gnc_elem_var_ref2(gnc_elem_dict):
	""" Reference to object, by id and type """
	def __init__(self,name ='',rname='owner'):
		super(gnc_elem_var_ref2,self).__init__(name)
		self.ref=None
		self.rname=rname
		self.rtype=None
		self.dic['ref'] = None
	
	def create(self,oh,name):
		(tbl, key) = name.split(':')
		if tbl != self.rname:
			return gnc_unk_elem(name,self.name)
		if key == 'type':
			return gnc_elem_var(name)
		elif key == "id":
			return gnc_elem_var_id(name)
		return gnc_unk_elem(name,self.name)
	
	def end(self,oh,parent):
		# todo: verify dic['type'] = model..
		parent.setDict(oh,self.name.split(':')[1],(self.dic['id'],self.dic['ref'] ))
		#oh.print_item(self.name,self)

class GCContent(sax.handler.ContentHandler):

    def __init__(self,outhandler=GCDbgHandler()):
	self.outh=outhandler
	self.stack = []

    def startElement(self, name, attrs):
        #global last_input_startElement
        #last_input_startElement = str(name.encode(lcodec))
	if self.stack:
		ni=self.stack[len(self.stack)-1].create(self.outh,name)
	elif name == "gnc-v2":
		ni = gnc_v2_elem(name)
	else:
		ni = gnc_unk_elem(name)
	self.stack.append(ni)
	ni.begin(self.outh,attrs)
	if len(self.stack)>200:
		raise Exception("Maximum stack exceeded")
 
    def endElement(self, name):
        #global last_input_endElement
        #last_input_endElement = str(name.encode(lcodec))

        def insert_statement(kind, value_dict):
	    pass
	if not self.stack:
		raise Exception("End element not in stack.")
	elif self.stack[len(self.stack)-1].name !=name:
		raise Exception("End of element mismatch!")
	
	el=self.stack.pop()
	if len(self.stack):
		el.end(self.outh,self.stack[len(self.stack)-1])
	else:
		if el.name != 'gnc-v2':
			self.outh.debug('Ending %s without parent'%el.name)
		el.end(self.outh,None)
	return
	
	if name == 'trn:date-posted':
            self.trn['date_ym'] = self.date_posted[0:7]
            self.trn['date_d'] = self.date_posted[8:10]
            self.status_date_posted = False
            self.date_posted = ''

    def characters(self, content):
	cnt=content.strip()
	if not cnt:
		return
	self.stack[len(self.stack)-1].getchars(self.outh,cnt)
	return
        if self.tbl == 'act':
            if self.key in self.account:
                self.account[self.key] += content
        elif self.tbl == 'trn':
            if self.key in self.trn:
                self.trn[self.key] += content
            elif self.key == 'date-posted':
                self.status_date_posted = True
        elif self.tbl == 'ts':
            if self.key == 'date' and self.status_date_posted == True:
                self.date_posted += content
        elif self.tbl == 'split':
            if self.key in self.split:
                self.split[self.key] += content
        elif self.tbl == 'gnc':
            if self.key == 'template-transactions':
                self.status_template_trns = True
