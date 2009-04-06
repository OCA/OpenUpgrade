# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2009 P.Christeas <p_christ@hol.gr>. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import wizard
import tools
import base64
import pooler
from tempfile import TemporaryFile
import gnccontent
from xml import sax
import netsvc

view_form="""<?xml version="1.0"?>
<form string="Import GnuCash Data">
    <group colspan="2" col="4">
        <separator string="Import new language" colspan="4"/>
        <label string="You can upload, analyze and import a GnuCash file from here." colspan="4"/>
        <field name="data" colspan="4"/>
	<field name="account" colspan="4"/>
    </group>
</form>"""

fields_form={
    #'name':{'string':'Language name', 'type':'char', 'size':64, 'required':True},
    'data':{'string':'File', 'type':'binary', 'required':True},
    'account': { 'string': 'Use account', 'type': 'many2one', 'relation': 'account.account',
        'domain': "[('type','=','view'),('parent_id','=',None)]",
    	'help': 'If book has not been used before, merge it into that account', }
    }

def get_first(tup):
	"""Convenience function that returns the first part of a tuple"""
	return tup[0]

def fnc_date_only(val,gnco,gnself):
	return val.date().isoformat()

def cas_get_ref(c, a, s):
	if c:
		return c[1]
	else:
		return None

def cas_get_res_id(c, a, s):
	if c:
		return c[1]['res_id']
	else:
		return None

class GCHandler (gnccontent.GCDbgHandler):
	"""This backend syncs the Gnucash object into the OpenERP ones.
	   It should have a lifetime within the import process.
	"""
	def __init__(self,cr,uid):
		super(GCHandler,self).__init__()
		self.logger=netsvc.Logger()
		self.cr = cr
		self.uid= uid
		self.pool=pooler.get_pool(cr.dbname)
		self.iobj= self.pool.get('gnucash.index')
		self.def_book=None
		self.dbglims= {}
		self.cur_book=None
		self.cur_company=None
		self.sync_mark=0
		self.syncLimit=3000
		self.notProc=0
		self.act_types= [ { 'gnc': None, 'user_type': 'view'},
			{ 'gnc': 'CASH','type': 'other', 'user_type': 'cash'},
			{ 'gnc': 'BANK','type': 'other', 'user_type': 'asset'},
			{ 'gnc': 'ASSET','type': 'other', 'user_type': 'asset'},
			{ 'gnc': 'LIABILITY','type': 'other', 'user_type': 'liability'},
			{ 'gnc': 'INCOME','type': 'receivable', 'user_type': 'income'},
			{ 'gnc': 'EXPENSE','type': 'payable', 'user_type': 'expense'},
			{ 'gnc': 'EQUITY','type': 'other', 'user_type': 'equity'},
			{ 'gnc': 'CREDIT','type': 'other', 'user_type': 'credit'} ]

	def dprint(self,*args):
		self.logger.notifyChannel('gnucash', netsvc.LOG_INFO, ' '.join(map(lambda a: str(a), args)))
	def debug(self,stri):
		self.logger.notifyChannel('gnucash', netsvc.LOG_DEBUG,stri)
	def debug_lim(self,domain,stri):
		if self.dbglims.has_key(domain):
			if self.dbglims[domain] >= 20:
				self.dbglims[domain]+=1
				if (self.dbglims[domain] % 100) == 0:
					self.logger.notifyChannel('gnucash', netsvc.LOG_DEBUG,stri[:30]+'... mark.'+str(self.dbglims[domain]))
				return
			self.dbglims[domain]+=1
		else:
			self.dbglims[domain]=0
		self.logger.notifyChannel('gnucash', netsvc.LOG_DEBUG,stri)
	def warn(self,stri):
		self.logger.notifyChannel('gnucash', netsvc.LOG_WARNING,stri)
	
	def fill_idref(self,idv,obj):
		if not idv.val:
			return
		if ( self.sync_mark > self.syncLimit):
			return None
		ooids = self.iobj.search(self.cr, self.uid, [('guid', '=',idv.val)])
		if ooids:
		    oos = self.iobj.read(self.cr,self.uid,ooids,['guid','parent_book','module','model','res_id'])
		    #self.debug("For object %s %s, located:"%(obj.name,idv.val)+str(oos))
		    if len(oos) != 1:
			    self.warn("Found %d results instead of 1!"%len(oos))
		    else:
		    	idv.ref = {'module': oos[0]['module'], 'model': oos[0]['model'],'res_id': oos[0]['res_id']}
			return
		self.warn("Cannot locate guid = %s for %s@%s"%(idv.val,idv.name,obj.name))
		#raise Exception("Cannot locate guid = %s for %s@%s"%(idv.val,idv.name,obj.name))
	
	def get_acct_type(self,act):
		for ats in self.act_types:
			if ats['gnc'] == act:
				return ats['type']
		self.warn("Do not have item for Gnucash account type: \"%s\""%act)
		return 'other'
		 
	def get_acct_utype(self,act):
		for ats in self.act_types:
			if ats['gnc'] == act:
				if ats.has_key('user_tid'):
					return ats['user_tid']
				else:
					self.warn("Have no user_type for account type: %s"%ats['gnc'])
		return self.act_types[0]['user_tid']

	def start_book(self,book):
		self.debug("Start Gnucash book")
		if not self.act_types[0].has_key('user_tid'):
			obj = self.pool.get('account.account.type')
			oids = obj.search(self.cr,self.uid,[('code','in',map(lambda a: a['user_type'],self.act_types))])
			res = obj.read(self.cr,self.uid,oids,['id','code'])
			for r in res:
				for act in self.act_types:
					if r['code'] == act['user_type']:
						act['user_tid']= r['id']
			#self.debug("Now, account types are:" + str(self.act_types))

	def set_book(self,book):
		if self.cur_book:
			self.warn("Book set for a second time!")
		boi=self.iobj.search(self.cr, self.uid, [('guid', '=',book.bookid),('model','=','account.account')])
		if boi:
		    bos = self.iobj.read(self.cr,self.uid,boi,['guid','parent_book','module','model','res_id'])
		    if bos:
			    assert(bos[0]['module'] == 'account')
			    self.debug('Located existing book id=%d'%bos[0]['res_id'])
			    self.set_book2(bos[0])
			    return
		if not self.def_book:
			raise Exception(_("Default book not set and book GUID is not registered! Please create a book and specify it in the wizard."))
		self.debug("Must use default book %s"%str(self.def_book))
		cb={'guid': book.bookid, 'module': 'account','model':'account.account','res_id': self.def_book}
		self.iobj.create(self.cr,self.uid,cb)
		self.set_book2(cb)
		
	def set_book2(self,book):
		self.cur_book=book
		obj=self.pool.get('account.account')
		aid=obj.search(self.cr, self.uid, [('id','=',book['res_id'])])
		if aid:
			acc=obj.read(self.cr,self.uid,aid,['company_id'])
			self.cur_company=acc[0]['company_id'][0]
		
	def end_book(self,book):
		self.decCount('book')
		self.debug("End Gnucash book")
		dd = {}
		for key,val in self.counters.iteritems():
			if val:
				dd[str(key)] = val
		self.dprint('Counters left:',dd)
		self.dprint('Not processed since 3k limit:',self.notProc)
		self.cur_book=None
		self.cur_company=None
	
	def end_account(self,act,par):
		self.decCount('account')
		self.sync('account','account.account',act,
			[('name','name'),
			    ('code','code',lambda c,a,s: c or a.dic['id'][:6]),
			    ('type','type',lambda c,a,s: s.get_acct_type(c)),
			    ('user_type','type',lambda c,a,s: s.get_acct_utype(c),get_first),
			    ('parent_id','parent', lambda c,a,s: s.get_parent('account.account',c,a) or s.cur_book['res_id'], get_first),
			    ('company_id','',lambda c,a,s: s.cur_company,get_first)
			    ])
		
	def end_invoice(self,act,par):
		self.decCount('gnc:GncInvoice')
		try:
			if (act.dic['owner'][1]):
			    adre =act.dic['owner'][1]
			    if adre['model'] != 'res.partner':
				    self.warn('invalid model in partner ref: %s' % adre['model'])
				    raise Exception()
			    addrs=self.pool.get('res.partner.address').search(self.cr, self.uid,
				[ ('partner_id','=',adre['res_id']), ('active','=','t')])
			    if addrs:
				# print "Located addresses:", addrs
				act.dic['address']=addrs[0]	# arbitrarily select the first
			    else:
				self.warn("No address for partner id=%s" % str(act.dic['owner'][1]))
		except:
			self.warn("Cannot get address for partner id=%s" % str(act.dic['owner'][1]))
	
		self.sync('invoice','account.invoice',act,
			[('name','name'),
			    ('number','inv_ref'),
			    ('comment','notes'),
			    ('reference', 'billing_id'),
			    ('partner_id', 'owner', cas_get_res_id, get_first ),
			    ('state','active', lambda c,a,s: (c and 'open') or 'cancel'),
			    ('currency_id', 'currency', lambda c,a,s: c['ref'], get_first),
			    ('address_invoice_id', 'address', None, get_first),
			    ('account_id', 'postacc', cas_get_res_id, get_first ),
			    ('date_invoice','posted', fnc_date_only ),
			    ])

	def end_entry(self,act,par):
		self.decCount('gnc:GncEntry')
		self.sync('entry','account.invoice.line',act,
			[('name','description'),
			    ('invoice_id', 'invoice', cas_get_res_id, get_first ),
			    ('quantity','qty'),
			    ('discount', 'i-discount'),
			    ('account_id', 'i-acct', cas_get_res_id, get_first ),
			    ('price_unit', 'i-price'),
			    #('note', '', lambda c,a,s: unicode(a.dic))
			])

	def get_parent(self, oo_model, fldt, gnc):
		if not fldt or fldt == None:
			return None
		if len(fldt)<2 or fldt[1] == None:
			return None
		fld=fldt[1]
		
		if type(fld) != type({}):
			raise Exception('Parent field is %s: %s'%(str(type(fld)),str(fld)))
		if not fld.has_key('model') or fld['model'] != oo_model:
			raise Exception('Model mismatch for %s in %s'%(oo_model,str(fld)))
		if not fld.has_key('res_id'):
			raise Exception('Unresolved guid for %s: %s'%(gnc.name,str(fld)))
		return fld['res_id']

	def sync(self,oo_module, oo_model,gnco,fields=[], match_fields = []):
		if not fields:
			raise Exception('No fields specified')
		if ( self.sync_mark > self.syncLimit):
			self.notProc=self.notProc+1
			return None
		
		obj = self.pool.get(oo_model)
		if gnco.dic.has_key('guid'):
			guid=gnco.dic['guid']
		else:
			guid=gnco.dic['id']
		goi=self.iobj.search(self.cr, self.uid, [('guid', '=',guid),('model','=',oo_model)])
		found = False
		
		if not goi and (len(match_fields)>0):
			match_arr=[]
			for fld in match_fields:
				if len(fld)>2 and fld[2]:
					fnc= fld[2]
				else:
					fnc = lambda a,b,c: a
				val=None
				if fld[1] in gnco.dic:
					val = gnco.dic[fld[1]]
				match_arr.append( (fld[0],'=',fnc(val,gnco,self)) )
			self.dprint("Retrying match with: "+str(match_arr))
			res = obj.search(self.cr, self.uid, match_arr)
			if res:
				gos= self.iobj.create(self.cr,self.uid, {'guid': guid, 'parent_book': self.cur_book['res_id'], 'module': oo_module,'model':oo_model,'res_id': res[0]})
				goi= [gos,]
		
		if goi:
		    gos = self.iobj.read(self.cr,self.uid,goi,['guid','parent_book','module','model','res_id', 'noupdate'])
		    if gos:
			    #assert(gos[0]['module'] == 'account', gos[0]['module'])
			    #assert(gos[0]['parent_book'] == self.cur_book['res_id'],str(gos[0]['parent_book'])+" != "+str(self.cur_book['res_id']))
			
			    ooit= obj.read(self.cr,self.uid,gos[0]['res_id'],map(lambda x: x[0], fields))
			    #for ooit in oos:
			    if True:
				if ooit['id'] == gos[0]['res_id']:
					found = True
					if gos[0]['noupdate']:
						self.debug("record %s[%s] is \"noupdate\", won't sync" % (gos[0]['model'], gos[0]['res_id']))
						return ooit['id']
					oocp = {}
					for fld in fields:
						if len(fld)>2 and fld[2]:
							fnc= fld[2]
						else:
							fnc = lambda a,b,c: a
						if len(fld)>3 and fld[3]:
							fno= fld[3]
						else:
							fno= lambda a: a
						val=None
						if fld[1] in gnco.dic:
							val = gnco.dic[fld[1]]
						if fno(ooit[fld[0]]) != fnc(val,gnco,self):
							oocp[fld[0]] = fnc(val,gnco,self)
					if oocp:
						#self.upd+=1
						self.sync_mark=self.sync_mark+1
						self.debug_lim(oo_model,"Must update: %s" % str(oocp))
						obj.write(self.cr,self.uid, [ooit['id']],oocp)
						
					return ooit['id']
	
		if not found:
			#self.new+=1
			oonew = { }
			for fld in fields:
				if len(fld)>2 and fld[2]:
					fnc= fld[2]
				else:
					fnc = lambda a,b,c: a
				#if len(fld)>3 and fld[3]:
					#fno= fld[3]
				#else:
					#fno= lambda a: a
				val=None
				if fld[1] in gnco.dic:
					val = gnco.dic[fld[1]]
				oonew[fld[0]] = fnc(val,gnco,self)
			self.sync_mark=self.sync_mark+1
			self.debug_lim(oo_model,"must create: %s" %str(oonew))
			res = obj.create(self.cr,self.uid,oonew)
			self.debug_lim(oo_model,"created: %s #%s"%(oo_model,str(res)))
			self.iobj.create(self.cr,self.uid, {'guid': guid, 'parent_book': self.cur_book['res_id'], 'module': oo_module,'model':oo_model,'res_id': res})
			return res

	def end_transaction(self,trn,par):
		self.decCount('transaction')
		#place the period inside the dic, because we will need it again.
		trn.dic['period_id']=self.find_period(trn.dic['date-posted'])
		mid= self.sync('account','account.move',trn,
			[('name','description'), ('journal_id','',lambda c,a,s: 4,get_first),
			('date','date-posted',fnc_date_only), ('period_id','period_id',None ,get_first)
			])
		for spld in trn.splits:
			split = gnccontent.gnc_elem_dict('split')
			split.dic = spld
			split.dic['name']= spld.get('memo',trn.dic['description'][:64])
			split.dic['period_id']=trn.dic['period_id']
			split.dic['move_id'] = mid
			if split.dic['value'] >= 0.0:
				split.dic['ocredit'] =  split.dic['value']
				split.dic['odebit'] = 0.0
			else:
				split.dic['ocredit'] = 0.0
				split.dic['odebit'] = 0.0 - split.dic['value']
			split.dic['date_created'] = trn.dic.get('date-entered',None)
			#self.debug_lim('split',str(split.dic))
			self.sync('account','account.move.line',split,
				[('name','name'),('period_id','period_id',None ,get_first),
				('journal_id','',lambda c,a,s: 4,get_first),
				('account_id','account',lambda c,a,s: s.get_parent('account.account',c,a), get_first),
				('move_id','move_id',None,get_first),
				('debit','odebit'),('credit','ocredit')])
			

	def find_period(self,date):
		per=self.pool.get('account.period').find(self.cr, self.uid,date)
		if per:
			return per[0]
		else:
			return False
	
	def _end_partner(self, act, mfields=[]):
		fields= [('name','name'), ('active','active')]
		fields.extend(mfields)
		self.sync('base','res.partner',act, fields, [('name','name')])
		
	def end_vendor(self,act,par):
		self.decCount('gnc:GncVendor')
		self._end_partner(act,[('supplier',None,lambda c,a,s: True)])

	def end_customer(self,act,par):
		self.decCount('gnc:GncCustomer')
		self._end_partner(act,[('customer',None,lambda c,a,s: True)])

	def find_commodity(self,com):
		self.decCount('commodity')
		if com['space'] != 'ISO4217' : #commodity is a currency
			return
		
		per=self.pool.get('res.currency').\
			search(self.cr, self.uid,[('code','=',com['id'])] )
		print "Currency located:", per
		if per:
			return per[0]
		else:
			return False

class wizard_import_gnucash(wizard.interface):

    def _import_gnucash(self, cr, uid, data, context):
        form=data['form']
        fileobj = TemporaryFile('w+')
        fileobj.write( base64.decodestring(form['data']) )

        # now we determine the file format
        fileobj.seek(0)
        try:
            gch=GCHandler(cr,uid)
            gch.def_book=form['account']
            handler = gnccontent.GCContent(gch);
            sax.parse(fileobj,handler)
        except sax._exceptions.SAXParseException, exc:
            raise Exception("Parse exception: %s at %d,%d\n" % (exc.getMessage(), exc.getLineNumber(),exc.getColumnNumber()))
        finally:
            fileobj.close()
        return {}

    states={
        'init':{
            'actions': [],
            'result': {'type': 'form', 'arch': view_form, 'fields': fields_form,
                'state':[
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('finish', 'Ok', 'gtk-ok', True)
                ]
            }
        },
        'finish':{
            'actions':[],
            'result':{'type':'action', 'action':_import_gnucash, 'state':'end'}
        },
    }
wizard_import_gnucash('gnucash.iwiz')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

