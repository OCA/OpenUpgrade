##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
# Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                    Jordi Esteve <jesteve@zikzakmedia.com>
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

import wizard
import pooler
import tools

sms_send_form = '''<?xml version="1.0"?>
<form string="%s">
	<separator string="%s" colspan="4"/>
	<field name="app_id"/>
	<newline/>
	<field name="user"/>
	<field name="password"/>
	<newline/>
	<field name="email_http"/>
	<field name="email"/>
	<separator colspan="4"/>
	<label string="Message:"/>
	<field name="default"/>
	<field name="text" nolabel="1" colspan="4"/>

	<separator string="The following tags can be included in the message. They will be replaced to the corresponding values of each partner contact:" colspan="4"/>
	<label string="[[partner_id]] -> Partner name" colspan="2"/>
	<label string="[[name]] -> Contact name" colspan="2"/>
	<label string="[[function]] -> Function" colspan="2"/>
	<label string="[[title]] -> Title" colspan="2"/>
	<label string="[[street]] -> Street" colspan="2"/>
	<label string="[[street2]] -> Street 2" colspan="2"/>
	<label string="[[zip]] -> Zip code" colspan="2"/>
	<label string="[[city]] -> City" colspan="2"/>
	<label string="[[state_id]] -> State" colspan="2"/>
	<label string="[[country_id]] -> Country" colspan="2"/>
	<label string="[[email]] -> Email" colspan="2"/>
	<label string="[[phone]] -> Phone" colspan="2"/>
	<label string="[[fax]] -> Fax" colspan="2"/>
	<label string="[[mobile]] -> Mobile" colspan="2"/>
	<label string="[[birthdate]] -> Birthday" colspan="2"/>
</form>''' % ('SMS - Gateway: clickatell','Bulk SMS send')

sms_send_fields = {
	'app_id': {'string':'API ID', 'type':'char', 'required':True},
	'user': {'string':'Login', 'type':'char', 'required':True},
	'password': {'string':'Password', 'type':'char', 'required':True},
	'email_http': {'string':'Email connection', 'type':'boolean', 'help':'HTTP or Email connection to clickatell gateway'},
	'email': {'string':"Sender's email", 'type':'char', 'help':'Only required for Email connection to clickatell gateway', 'size':128},
	'default': {'string':'Only send to default addresses', 'type':'boolean'},
	'text': {'string':'SMS Message', 'type':'text', 'required':True}
}

sms_done_form = '''<?xml version="1.0"?>
<form string="SMS">
	<field name="sms_sent"/>
</form>'''

sms_done_fields = {
	'sms_sent': {'string':'Quantity of SMS sent', 'type':'integer', 'readonly': True},
}


def _sms_send(cr, uid, data, context, adr):
	import re
	# change the [[field]] tags with the partner address values
	pattern = re.compile('\[\[\S+\]\]')
	fields = pattern.findall(data['form']['text'])
	texts = []
	for field in fields:
		text = getattr(adr, field[2:-2])
		if text and field[-5:-2]=='_id': # State or country
			text = text.name
		texts.append(text or '')
	sms = pattern.sub('%s', data['form']['text'])
	sms = sms % tuple(texts)
	#print sms

	to = adr.mobile
	to = to.replace(' ','')
	if adr.country_id and adr.country_id.code in ('ES', 'CT') and to[:1] == '6': # Spain mobiles begin with 6
		to = '34'+to
	sms = ' '.join( sms.split('\n') ) # Conversion of '\n' to ' ' is necessary
	sms_sent = unicode(sms, 'utf-8').encode('latin1')
	if data['form']['email_http']:
		# Connection by Email
		text = 'user:' + data['form']['user'] + '\npassword:' + data['form']['password'] + '\napi_id:' + data['form']['app_id'] + '\nto:' + to + '\ntext:' + sms_sent
		#print text
		tools.email_send(data['form']['email'], ['sms@messaging.clickatell.com'], '', text)
	else:
		# Connection by http
		tools.sms_send(data['form']['user'], data['form']['password'], data['form']['app_id'], sms_sent, to)

	# Add a partner event
	c_id = pooler.get_pool(cr.dbname).get('res.partner.canal').search(cr ,uid, [('name','ilike','SMS'),('active','=',True)])
	c_id = c_id and c_id[0] or False
	pooler.get_pool(cr.dbname).get('res.partner.event').create(cr, uid,
			{'name': 'SMS sent',
			 'partner_id': adr.partner_id.id,
			 'description': sms,
			 'canal_id': c_id,
			 'user_id': uid, })


def _sms_send_partner(self, cr, uid, data, context):
	nbr = 0
	criteria = [('partner_id','in',data['ids'])]
	if data['form']['default']: # Only default addresses
		criteria.append(('type','=','default'))
	adr_ids = pooler.get_pool(cr.dbname).get('res.partner.address').search(cr ,uid, criteria)
	addresses = pooler.get_pool(cr.dbname).get('res.partner.address').browse(cr, uid, adr_ids, context)
	for adr in addresses:
		if adr.mobile:
			_sms_send(cr, uid, data, context, adr)
			nbr += 1
	return {'sms_sent': nbr}

class part_sms(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'form', 'arch':sms_send_form, 'fields': sms_send_fields, 'state':[('end','Cancel'), ('send','Send SMS')]}
		},
		'send': {
			'actions': [_sms_send_partner],
			'result': {'type': 'form', 'arch': sms_done_form, 'fields': sms_done_fields, 'state': [('end', 'End')] }
		}
	}
part_sms('res.partner.sms_send_2')


def _sms_send_partner_address(self, cr, uid, data, context):
	nbr = 0
	criteria = [('id','in',data['ids'])]
	if data['form']['default']: # Only default addresses
		criteria.append(('type','=','default'))
	adr_ids = pooler.get_pool(cr.dbname).get('res.partner.address').search(cr ,uid, criteria)
	addresses = pooler.get_pool(cr.dbname).get('res.partner.address').browse(cr, uid, adr_ids, context)
	for adr in addresses:
		if adr.mobile:
			_sms_send(cr, uid, data, context, adr)
			nbr += 1
	return {'sms_sent': nbr}

class part_sms_partner_address(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'form', 'arch':sms_send_form, 'fields': sms_send_fields, 'state':[('end','Cancel'), ('send','Send SMS')]}
		},
		'send': {
			'actions': [_sms_send_partner_address],
			'result': {'type': 'form', 'arch': sms_done_form, 'fields': sms_done_fields, 'state': [('end', 'End')] }
		}
	}
part_sms_partner_address('res.partner.address.sms_send')