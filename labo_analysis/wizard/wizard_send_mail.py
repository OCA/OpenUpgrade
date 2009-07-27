
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: wizard_spam.py 1005 2005-07-25 08:41:42Z nicoe $
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
import binascii
import wizard
import pooler
import tools
import base64	
email_send_form = '''<?xml version="1.0"?>
<form string="Mass Mailing">
	<field name="from"/>
	<newline/>
	<field name="subject"/>
	<newline/>
	<field name="text"/>
	<newline/>
	<field name="attach"/>
</form>'''

email_send_fields = {
	'from': {'string':"Sender's email", 'type':'char', 'size':64, 'required':True},
	'subject': {'string':'Subject', 'type':'char', 'size':64, 'required':True},
	'text': {'string':'Message', 'type':'text_tag', 'required':True},
	'attach':{'string':'Attachment', 'type':'many2one','relation':'ir.attachment'}
}

# this sends an email to ALL the addresses of the selected partners.
def _mass_mail_send(self, cr, uid, data, context):
	nbr = 0
	partners = pooler.get_pool(cr.dbname).get('labo.analysis.request').browse(cr, uid, data['ids'], context)
	for p in partners:
		partner=p.ref_client
		for adr in partner.address:
			if adr.email:
				name = adr.name or partner.name
				to = '%s <%s>' % (name, adr.email)
#TODO: add some tests to check for invalid email addresses
#CHECKME: maybe we should use res.partner/email_send
				attach_ids = pooler.get_pool(cr.dbname).get('ir.attachment').search(cr, uid,
							[('res_model', '=', 'labo.analysis.request'),
								('res_id', '=', p.id)])
				res = pooler.get_pool(cr.dbname).get('ir.attachment').read(cr, uid,
							attach_ids, ['datas_fname','datas'])
				res = map(lambda x: (x['datas_fname'],
						base64.decodestring(x['datas'])), res)
				tools.email_send_attach(data['form']['from'], [to], data['form']['subject'], data['form']['text'],attach=res)
				nbr += 1
	#	pooler.get_pool(cr.dbname).get('res.partner.event').create(cr, uid,
	#			{'name': 'Email sent through mass mailing',
	#			 'partner_id': partner,
	#			 'description': data['form']['text'], })
#TODO: log number of message sent
	return {'email_sent': nbr}


class part_email(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'form', 'arch': email_send_form, 'fields': email_send_fields, 'state':[('end','Cancel'), ('send','Send Email')]}
		},
		'send': {
			'actions': [_mass_mail_send],
			'result': {'type': 'state', 'state':'end'}
		}
	}
part_email('labo.analysis.spam_send')
