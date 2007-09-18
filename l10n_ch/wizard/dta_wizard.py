# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import pooler
import wizard
import base64 
from osv import osv
import time
import pooler
import mx.DateTime
from mx.DateTime import RelativeDateTime, DateTime





res_form = """<?xml version="1.0"?>
<form string="DTA file creation - Results">
<separator colspan="4" string="Clic on 'Save as' to save the DTA file :" />
	<field name="dta"/>
	<separator string="Logs" colspan="4"/>
	<field name="note" colspan="4" nolabel="1"/>
</form>
"""

res_fields = {
	'dta' : {
		'string':'DTA File',
		'type':'binary',
		'readonly':True,
	},
	'note' : {'string':'Log','type':'text'}
}

res_states= []

trans=[(u'é','e'),
	   (u'è','e'),
	   (u'à','a'),
	   (u'ê','e'),
	   (u'î','i'),
	   (u'ï','i'),
	   (u'â','a'),
	   (u'ä','a')]
def tr(s):
	s= s.decode('utf-8')

	for k in trans:
		s = s.replace(k[0],k[1])

	try:
		res= s.encode('ascii','replace')
	except:
		res = s
	return res
		
class record:
	def __init__(self,global_context_dict):

		for i in global_context_dict:
			global_context_dict[i]= global_context_dict[i] and tr(global_context_dict[i])
		self.fields = []
		self.global_values = global_context_dict
		self.pre={'padding':'','seg_num1':'01','seg_num2':'02',
				  'seg_num3':'03','seg_num4':'04','seg_num5':'05',
				   'flag':'0', 'zero5':'00000'
						   }
		self.post={'date_value_hdr':'000000','type_paiement':'0'}
		self.init_local_context()

	def init_local_context(self):
		"""
		Must instanciate a fields list, field = (name,size)
		and update a local_values dict.
		"""
		raise "not implemented"

	def generate(self):
		res=''
		for field in self.fields :
			if self.pre.has_key(field[0]):
				value = self.pre[field[0]]
			elif self.global_values.has_key(field[0]):
				value = self.global_values[field[0]]
			elif self.post.has_key(field[0]):
				value = self.post[field[0]]
			else :
				pass
				#raise Exception(field[0]+' not found !')

			try:
				res = res + c_ljust(value, field[1])
			except :
				pass
			
		return res

class record_gt826(record):
	# -> bvr
	def init_local_context(self):
		self.fields=[
			('seg_num1',2),
			#header
			('date_value_hdr',6),('partner_bank_clearing',12),('zero5',5),('creation_date',6),
			('comp_bank_clearing',7), ('uid',5), 
			('sequence',5),
			('genre_trans',3),
			('type_paiement',1),('flag',1),
			#seg1
			('comp_dta',5),('invoice_number',11),('comp_bank_iban',24),('date_value',6),
			('invoice_currency',3),('amount_to_pay',12),('padding',14),
			#seg2
			('seg_num2',2),('comp_name',20),('comp_street',20),('comp_zip',10),
			('comp_city',10),('comp_country',20),('padding',46),
			#seg3
			('seg_num3',2),('partner_bvr',12),#numero d'adherent bvr
			('partner_name',20),('partner_street',20),('partner_zip',10),
			('partner_city',10),('partner_country',20),
			('invoice_bvr_num',27),#communication structuree
			('padding',2),#cle de controle
			('padding',5)
			]

		self.pre.update({'date_value_hdr': self.global_values['date_value'],
						 'date_value':'',
						 'partner_bank_clearing':'','partner_cpt_benef':'',
						 'genre_trans':'826',
						 'conv_cours':'', 'option_id_bank':'D',
						 'partner_bvr' : '/C/'+ self.global_values['partner_bvr'],
						 'ref2':'','ref3':'', 
						 'format':'0'})

class record_gt827(record):
	# -> interne suisse (bvpost et bvbank)
	def init_local_context(self):
		self.fields=[
			('seg_num1',2),
			#header
			('date_value_hdr',6),('partner_bank_clearing',12),('zero5',5),('creation_date',6),
			('comp_bank_clearing',7), ('uid',5), 
			('sequence',5),
			('genre_trans',3),
			('type_paiement',1),('flag',1),
			#seg1
			('comp_dta',5),('invoice_number',11),('comp_bank_iban',24),('date_value',6),
			('invoice_currency',3),('amount_to_pay',12),('padding',14),
			#seg2
			('seg_num2',2),('comp_name',20),('comp_street',20),('comp_zip',10), 
			('comp_city',10),('comp_country',20),('padding',46),
			#seg3
			('seg_num3',2),('partner_bank_number',30),
			('partner_name',24),('partner_street',24),('partner_zip',12),
			('partner_city',12),('partner_country',24),
			#seg4
			('seg_num4',2),('partner_comment',112),('padding',14),
			#seg5
			#('padding',128)
			]

		self.pre.update({'date_value_hdr': self.global_values['date_value'],
						 'date_value':'',						 
						 'partner_cpt_benef':'',
						 'type_paiement':'0', 'genre_trans':'827',
						 'conv_cours':'', 'option_id_bank':'D',
						 'ref2':'','ref3':'', 
						 'format':'0'})




class record_gt836(record):
	# -> iban
	def init_local_context(self):
		self.fields=[
			('seg_num1',2),
			#header
			('date_value_hdr',6),('partner_bank_clearing',12),('zero5',5),('creation_date',6),
			('comp_bank_clearing',7), ('uid',5), 
			('sequence',5),
			('genre_trans',3),
			('type_paiement',1),('flag',1),
			#seg1
			('comp_dta',5),('invoice_number',11),('comp_bank_iban',24),('date_value',6),
			('invoice_currency',3),('amount_to_pay',15),('padding',11),
			#seg2
			('seg_num2',2),('conv_cours',12),('comp_name',35),('comp_street',35),('comp_country',3),('comp_zip',10),
			('comp_city',22),('padding',9),
			#seg3
			('seg_num3',2),('option_id_bank',1),('partner_bank_ident',70),
			('partner_bank_iban',34),('padding',21),
			#seg4
			('seg_num4',2),('partner_name',35),('partner_street',35),('partner_country',3),('partner_zip',10),('partner_city',22),
			('padding',21),
			#seg5
			('seg_num5',2),('option_motif',1),('invoice_reference',105),('format',1),('padding',19)
		]

		self.pre.update( {
			'partner_bank_clearing':'','partner_cpt_benef':'',
			'type_paiement':'0','genre_trans':'836',
			'conv_cours':'',
			'invoice_reference': self.global_values['invoice_reference'] or self.global_values['partner_comment'],
			'ref2':'','ref3':'',
			'format':'0'
		})
		self.post.update({'comp_dta':'','option_motif':'U'})


class record_gt890(record):
	# -> total
	def init_local_context(self):
		self.fields=[
			('seg_num1',2),
			#header
			('date_value_hdr',6),('partner_bank_clearing',12),('zero5',5),('creation_date',6),
			('comp_bank_clearing',7), ('uid',5), 
			('sequence',5),
			('genre_trans',3),
			('type_paiement',1),('flag',1),
			#total
			('amount_total',16),('padding',59)]

		self.pre.update({'partner_bank_clearing':'','partner_cpt_benef':'',
							  'company_bank_clearing':'','genre_trans':'890'})
			
def c_ljust(s, size):
	"""
	check before calling ljust
	"""
	s= s or ''
	if len(s) > size:
		s= s[:size]
	s = s.decode('utf-8').encode('latin1','replace').ljust(size)
	return s


class Log:
	def __init__(self):
		self.content= ""
		self.error= False
	def add(self,s,error=True):
		self.content= self.content + s
		if error:
			self.error= error
	def __call__(self):
		return self.content


def _create_dta(self,cr,uid,data,context):

	v={}
	v['uid'] = str(uid)
	v['creation_date']= time.strftime('%y%m%d')
	log=Log()
	dta=''

	pool = pooler.get_pool(cr.dbname)
	payment= pool.get('payment.order').browse(cr,uid,data['id'],context)

	if not payment.mode or payment.mode.type.code != 'dta':
		return {'note':'No payment mode or payment type code invalid.'}
	bank= payment.mode.bank_id
	if not bank:
		return {'note':'No bank account for the company.'}

	v['comp_bank_name']= bank.bank and bank.bank.name or False
 	v['comp_bank_clearing'] = bank.clearing

	if not v['comp_bank_clearing']:
		return {'note':'You must provide a Clearing Number for your bank account.'}
	
	user = pool.get('res.users').browse(cr,uid,[uid])[0]
	company= user.company_id
	#XXX dirty code use get_addr
	co_addr= company.partner_id.address[0]
	v['comp_country'] = co_addr.country_id and co_addr.country_id.name or ''
	v['comp_street'] = co_addr.street or ''
	v['comp_zip'] = co_addr.zip
	v['comp_city'] = co_addr.city
	v['comp_name'] = co_addr.name
	
	v['comp_dta'] = ''#XXX not mandatory in pratice


	v['comp_bank_number'] = bank.acc_number or ''

	v['comp_bank_iban'] = bank.iban or ''
	if not v['comp_bank_iban'] : 
		return {'note':'No iban number for the company bank account.'}

	
	inv_obj = pool.get('account.invoice')
	dta_line_obj = pool.get('account.dta.line')
	res_partner_bank_obj = pool.get('res.partner.bank')

	seq= 1
	amount_tot = 0
	th_amount_tot= 0
	reconciles_and_st_lines= []


 	bk_st_id = pool.get('account.bank.statement').create(cr,uid,{
 		'journal_id': payment.mode.journal.id,
 		'balance_start':0,
 		'balance_end_real':0, 
 		'state':'draft',
 		})

	## Fetch the invoices:
	cr.execute('''select i.id,pl.id 
	              from payment_line pl
				   join account_move_line ml on (pl.move_line_id = ml.id)
				   join account_move m on (ml.move_id = m.id)
				   join account_invoice i on (i.move_id = m.id)
				   join payment_order p on (pl.order_id = p.id)
				  where p.id = %s
				  '''%payment.id)
	payment_lines= []
	invoices= []
	for i,p in cr.fetchall():
		payment_lines.append(p)
		invoices.append(i)
	line2inv= dict(zip(payment_lines,
					   pool.get('account.invoice').browse(cr,uid,invoices,context)))
	del payment_lines, invoices
	
	for pline in payment.line_ids:
		i = line2inv[pline.id]
		invoice_number = i.number or '??'
		if not pline.bank_id:
			log.add('\nNo partner bank defined. (partner: '+pline.partner_id.name+', entry:'+pline.move_line_id.name+').')
			continue
				
		
		v['sequence'] = str(seq).rjust(5).replace(' ','0')
		v['amount_to_pay']= str(pline.amount).replace('.',',')
		v['invoice_number'] = invoice_number or ''
		v['invoice_currency'] = i.currency_id.code or ''
		if not v['invoice_currency'] :
			log.add('\nInvoice currency code undefined. (partner: '+pline.partner_id.name+', entry:'+pline.move_line_id.name+', invoice '+invoice_number+').')
			continue

		
		v['partner_bank_name'] =  pline.bank_id.bank and pline.bank_id.bank.name or False
		v['partner_bank_clearing'] =  pline.bank_id.clearing or False
		if not v['partner_bank_name'] :
			log.add('\nPartner bank account not well defined, please provide a name for the associated bank (partner: '+pline.partner_id.name+', bank:'+res_partner_bank_obj.name_get(cr,uid,[pline.bank_id.id],context)[0][1]+').')
			continue

		v['partner_bank_iban']=  pline.bank_id.iban or False
		v['partner_bank_number']=  pline.bank_id.acc_number  and pline.bank_id.acc_number.replace('.','').replace('-','') or  False
		v['partner_post_number']=  pline.bank_id.post_number  and pline.bank_id.post_number.replace('.','').replace('-','') or  False
		
		v['partner_bvr']= pline.bank_id.bvr_number or ''
		
		if v['partner_bvr']:
			v['partner_bvr']= v['partner_bvr'].replace('-','')
			if len(v['partner_bvr']) < 9:
				v['partner_bvr']= v['partner_bvr'][:2]+ '0'*(9-len(v['partner_bvr'])) +v['partner_bvr'][2:]


		if pline.bank_id.bank:
			v['partner_bank_city'] = pline.bank_id.bank.city or False
			v['partner_bank_street'] = pline.bank_id.bank.street or ''
			v['partner_bank_zip'] = pline.bank_id.bank.zip or ''
			v['partner_bank_country'] = pline.bank_id.bank.country and \
					pline.bank_id.bank.country.name or ''

		v['partner_bank_code']= pline.bank_id.bank.bic
		v['invoice_reference']= i.reference
		v['invoice_bvr_num']= i.bvr_ref_num
		if v['invoice_bvr_num']:
			v['invoice_bvr_num'] = v['invoice_bvr_num'].replace(' ', '').rjust(27).replace(' ','0')
			
		v['partner_comment']= i.partner_comment
		v['partner_name'] = pline.partner_id and pline.partner_id.name or ''
		if pline.partner_id and pline.partner_id.address and pline.partner_id.address[0]:
			v['partner_street'] = pline.partner_id.address[0].street
			v['partner_city']= pline.partner_id.address[0].city
			v['partner_zip']= pline.partner_id.address[0].zip
			# If iban => country=country code for space reason
			elec_pay = pline.bank_id.state #Bank type
			if elec_pay == 'iban':
				v['partner_country']= pline.partner_id.address[0].country_id and pline.partner_id.address[0].country_id.code+'-' or ''
			else:
				v['partner_country']= pline.partner_id.address[0].country_id and pline.partner_id.address[0].country_id.name or ''
		else:
			v['partner_street'] =''
			v['partner_city']= ''
			v['partner_zip']= ''
			v['partner_country']= ''
			log.add('\nNo address for the partner: '+pline.partner_id.name)


		date_value= False
		if payment.date_prefered == 'fixed' and payment.date_planned:
			date_value = payment.date_planned
		elif payment.date_prefered == 'due':
			date_value = pline.due_date

		if date_value :
			date_value = mx.DateTime.strptime( date_value,'%Y-%m-%d') or  mx.DateTime.now()
			v['date_value'] = date_value.strftime("%y%m%d")
		else:
			v['date_value'] = "000000"

		# si compte iban -> iban (836)
		# si payment structure  -> bvr (826)
		# si non -> (827) 

		if elec_pay == 'dta_iban':
			# If iban => country=country code for space reason
			v['comp_country'] = co_addr.country_id and co_addr.country_id.code+'-' or ''
			record_type = record_gt836
			if not v['partner_bank_iban']:
				log.add('\nNo iban number for the partner bank:' + \
						res_partner_bank_obj.name_get(cr, uid, [pline.bank_id.id],
							context)[0][1] + \
									' (partner: ' + pline.partner_id.name + ').')
				continue

			if v['partner_bank_code'] : # bank code is swift (BIC address)
				v['option_id_bank']= 'A'
				v['partner_bank_ident']= v['partner_bank_code']
			elif v['partner_bank_city']:

				v['option_id_bank']= 'D'
				v['partner_bank_ident']= v['partner_bank_name'] +' '+v['partner_bank_street']\
					+' '+v['partner_bank_zip']+' '+v['partner_bank_city']\
					+' '+v['partner_bank_country']
			else:
				log.add("\nYou must provide the bank city "
				"or the bic code for the partner bank:" + \
						res_partner_bank_obj.name_get(cr, uid, [pline.bank_id.id],
							context)[0][1] + \
									' (partner: ' + pline.partner_id.name + ').')
				continue

			
		elif elec_pay == 'bvrbank' or elec_pay == 'bvrpost':
			if not v['invoice_bvr_num']:
				log.add('\nYou must provide a Bvr reference number. (invoice '+ invoice_number +')')
				continue
			if not v['partner_bvr']:
				log.add("\nYou must provide a BVR number "
				"on the partner bank:" + \
						res_partner_bank_obj.name_get(cr, uid, [pline.bank_id.id],
							context)[0][1] + \
									' (partner: ' + pline.partner_id.name + ').')
				continue
			record_type = record_gt826


		elif elec_pay == 'bvbank':
			if not v['partner_bank_number'] :
				if  v['partner_bank_iban'] :
					v['partner_bank_number']= v['partner_bank_iban'] 
				else:
					log.add('\nYou must provide a bank number in the partner bank. (invoice '+ invoice_number +')')
					continue

			if not  v['partner_bank_clearing']:
				log.add('\nPartner bank must have a Clearing Number for a BV Bank operation. (invoice '+ invoice_number +')')
				continue
			v['partner_bank_number'] = '/C/'+v['partner_bank_number']
 			record_type = record_gt827
			
 		elif elec_pay == 'bvpost':
			if not v['partner_post_number']:
				log.add('\nYou must provide a post number in the partner bank. (invoice '+ invoice_number +')')
				continue
			v['partner_bank_clearing']= ''
			v['partner_bank_number'] = '/C/'+v['partner_post_number']
 			record_type = record_gt827
			
		else:
			log.add('\nBank type not supported. (partner:'+ pline.partner_id.name +\
					', bank:' + \
					res_partner_bank_obj.name_get(cr, uid, [pline.bank_id.id],
						context)[0][1] + \
						', type:' + elec_pay + ')')
			continue


		try:
			dta_line = record_type(v).generate()
		except Exception,e :
			log.add('\nERROR:'+ str(e)+'(invoice '+ invoice_number+')')
			raise
			continue

		#logging
		log.add("Invoice : %s, Amount paid : %d %s, Value date : %s, State : Paid."%\
			  (invoice_number,pline.amount,v['invoice_currency'],date_value and\
			   date_value.strftime("%Y-%m-%d") or 'Empty date'),error=False)

		reconciles_and_st_lines.append((
			{'name': time.strftime('%Y-%m-%d'),
			 'line_ids': [(6, 0, i.move_line_id_payment_get(cr, uid, [i.id]))],
			},
			{'name':i.number,
			 'date': time.strftime('%Y-%m-%d'),
			 'amount': -pline.amount,
			 'type':{'out_invoice':'customer','in_invoice':'supplier',
					 'out_refund':'customer','in_refund':'supplier'}[i.type],
			 'partner_id':pline.partner_id.id,
			 'account_id':i.account_id.id,
			 'statement_id': bk_st_id,
			 
			}))

		dta = dta + dta_line
		amount_tot += pline.amount
		seq += 1
		
	
	# segment total
	v['amount_total'] = str(amount_tot).replace('.',',')
	v['sequence'] = str(seq).rjust(5).replace(' ','0')	
	try:
		if dta :
			dta = dta + record_gt890(v).generate()
	except Exception,e :
		log.add('\n'+ str(e) + 'CORRUPTED FILE !\n')
		raise
		

	log.add("\n--\nSummary :\nTotal amount paid : %.2f\nTotal amount expected : %.2f"\
			%(amount_tot,th_amount_tot),error=False)

	if not log.error:
		dta_data= base64.encodestring(dta)
		if reconciles_and_st_lines:
			data['statement'] = {
				'journal_id': payment.mode.journal.id,
				'balance_start':0,
				'balance_end_real':0, 
				'balance_end_real': -amount_tot,
				'state':'draft',
			}

			data['reconciles_and_st_lines']= reconciles_and_st_lines
		pool.get('payment.order').set_done(cr,uid,data['id'],context)
	else:
		dta_data= False
	return {'note':log(), 'dta': dta_data}



def _open_statement(self, cr, uid, data, context):
	pool= pooler.get_pool(cr.dbname)
	if not 'statement' in data:
		raise wizard.except_wizard('Error', 'No statement generated.')
	statement_id= pool.get('account.bank.statement').create(cr,uid,data['statement'])

	for r,l in data['reconciles_and_st_lines']:
		r_id= pool.get('account.bank.statement.reconcile').create(cr, uid, r)
		l.update({'reconcile_id': r_id})
		l_id= pool.get('account.bank.statement.line').create(cr,uid,l)

	return {
		'name': 'Bank Statement',
		'view_type': 'form',
		'view_mode': 'form,tree',
		'res_model': 'account.bank.statement',
		'view_id': False,
		'type': 'ir.actions.act_window',
		'res_id': statement_id,
	}
	
class wizard_dta_create(wizard.interface):
	states = {
		'init' : {
			'actions' : [_create_dta],
			'result' : {'type' : 'form',
						'arch' : res_form,
						'fields' : res_fields,
						'state' : [('end', 'Quit'),
								   ('open','Generate statement')]}
		},
		'open' : {'actions': [],		
					   'result':{'type':'action',
								 'action':_open_statement,
								 'state':'end'}
					   }
			 
	}

wizard_dta_create('account.dta_create')
