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
import csv
import StringIO
import sys
import time
import os
import string
import errno
import psycopg
import shutil
from datetime import date
import types

_form_cont = '''<?xml version="1.0"?>
<form title="%s">
	<field name="file_type" />
	<newline/>
	<field name="attach" string="%s"/>
</form>''' % ('Attach', 'File to import')


_fields_cont = {
	'attach':{'string':'Attachment', 'type':'binary'},
	'file_type':{'string':'File Format', 'type':'selection', 'selection':[
			('xls','XLS'),
			('csv','CSV'),
			], 'required':True, 'default': lambda *a: 'xls'},

}

def row_field(row,fieldname):
	if (type(row) is dict) and fieldname :
		if row.has_key(fieldname):
			return str(row[fieldname]).decode('latin').encode('utf8')
	return ''

def row_field_date(row,fieldname):
	strDate = row_field(row,fieldname)
	if strDate:
		return _makeDate(strDate)
	return None

def _makeDate(sdate):
    sdate=str(sdate)
    if len(sdate) == 4:
        y,m,d = sdate[2:],sdate[1:2],sdate[0:1]
    elif len(sdate) == 5:
        y,m,d = sdate[3:],sdate[1:3],sdate[0:1]
    elif len(sdate) == 6:
        y,m,d = sdate[4:],sdate[2:4],sdate[0:2]
    elif len(sdate) == 7:
        y,m,d = sdate[0:2],sdate[3:5],sdate[6:]
    elif len(sdate) == 8:
        y,m,d = sdate[0:2],sdate[3:5],sdate[6:]
    elif len(sdate) == 10:
        y,m,d = sdate[0:4],sdate[5:7],sdate[8:10]
    else:
        raise Exception("Format de date non reconnu %s",sdate)
    return y,m,d

#def _makeDate(sdate):
#	sdate=str(sdate)
#	if len(sdate) == 4:
#		y,m,d = sdate[2:],sdate[1:2],sdate[0:1]
#	elif len(sdate) == 5:
#		y,m,d = sdate[3:],sdate[1:3],sdate[0:1]
#	elif len(sdate) == 6:
#		y,m,d = sdate[4:],sdate[2:4],sdate[0:2]
#	else:
#		raise Exception("Format de date non reconnu %s",sdate)
#
##	print y,m,d
#	return y,m,d
#
def import_attachment(self, cr, uid, data, context):
	fields ={#'mission_number':False,
			'dog_child': False,
			'lp_file':False,
			'lp_serv':False,
			'lp_doss':False,
			'dog_mother': False,
			'dog_father': False,
			'preleveur1_id':False,
		#	'preleveur2_id':False,
			'sample_id':False,
			'res_filiation':False,
			}
	fields_prelev=['name','code']
	labo_obj=pooler.get_pool(cr.dbname).get('labo.labo')
	req_obj=pooler.get_pool(cr.dbname).get('labo.analysis.request')
	sample_obj=pooler.get_pool(cr.dbname).get('labo.sample')
	dog_obj=pooler.get_pool(cr.dbname).get('labo.dog')
	partner_obj=pooler.get_pool(cr.dbname).get('res.partner')
	contact_obj=pooler.get_pool(cr.dbname).get('res.partner.address')
	flag=''
	content=base64.decodestring(data['form']['attach'])
	sheetnames = []

	if data['form']['file_type'] == 'xls':
		xl = tools.readexcel(file_contents = content)
		shname = xl.worksheets()
		for sh in shname:
			a = xl.getiter(sh)
			sheet_items = []
			for row in a:
				if len([i for i in row.values() if i]):
					print len(row),type(row)
					sheet_items.append(row)
			sheetnames.append(sheet_items)
#	else:
#		sh1 = csv.DictReader(content.split('\n'), delimiter=',')
#		csv_lines = []
#		for row in sh1:
#			csv_lines.append(row)
#		sheetnames.append(csv_lines)

#	"""
#	Following code is used for Extracting Data from Excel Files the using xlrd
#	"""
#	content=base64.decodestring(data['form']['attach'])
#	xl = tools.readexcel(file_contents = content)
#	sheetnames = xl.worksheets()
#
#	"""
#	Following code is used for the Importing a data from excel sheets to Labo Sample model
#	Its support multiple sheets also
#	"""
	for sheet in sheetnames:
		print "******************************************* No of records for Importing *******************************************", len(sheet)
		for line in sheet:
			print "LINEEEE", line['LPSERV']
			"""
			Set the labo. sample fields first ...
				'LPSERV':'lp_serv',
				'LPDOSS':'lp_doss',
				'LPCFIL':'res_filiation',
				'LPFILE':'lp_file',
				'LPDTRC':'date_reception',
			"""

			fields['lp_serv']=row_field(line,'LPSERV')
			fields['lp_doss']=row_field(line,'LPDOSS')
			fields['res_filiation'] = row_field(line, 'LPCFIL')
			fields['lp_file']=row_field(line,'LPFILE')
			fields['date_reception']=row_field_date(line,'LPDTRC')

#			"""
#			Set the preleveur2_id
#			"""
#
#			prelver2 = row_field(line,'LPENO2')
#			if prelver2:
#				prelev_id2=partner_obj.search(cr, uid, [('name', 'like', prelver2)])
#				if len(prelev_id2):
#					fields['preleveur2_id']=prelev_id2[0]
#				else:
#					fields['preleveur2_id'] = partner_obj.create(cr,uid,{'name': prelver2})
#
			"""
			Set the preleveur1_id

			"""
			prelver1 = row_field(line,'LPENOM')

			if prelver2:
				prelev_id=partner_obj.search(cr, uid, [('name', 'like', prelver1 )])
				if len(prelev_id):
					fields['preleveur1_id'] = prelev_id[0]
				else:
					fields['preleveur1_id']= partner_obj.create(cr,uid,{'name': row_field(line,'LPENOM'),'ref':row_field(line,'LPENUM')})
					city_zip=row_field(line,'LPELOC').split(' ')
					zip=city_zip[0] and city_zip[0] or ''
					city=len(city_zip)==2 and city_zip[1] and city_zip[1:] or ''
					new_contact_prelev=contact_obj.create(cr,uid,{'name': row_field(line,'LPENOM'),
																'city':city and city[0].replace('"',''),
																'street':row_field(line,'LPEADR'),
																'zip':zip and zip.replace('"',''),
																'partner_id':new_prelev
					})

			"""
			Set the Mother dog to labo sample
			   'LPFNOM':'dog_mother/name',
			   'LPFNUM':'dog_mother/pedigree',
			   'LPFTAT':'dog_mother/tatoo',
			   'LPFPUC':'dog_mother/ship',
			   'LPFNOR':'dog_mother/origin',
			   'LPFDTN':'dog_mother/birthdate',
			   'LPFRLB':'dog_mother/labo_id/ref',
			   'LPFLLB':'dog_mother/labo_id/name',
			   'LPFNLB':'dog_mother/labo_id/code',
			   'LPFNPR':'dog_mother/progenus_number',
			"""
			mothername = row_field(line,'LPFNOM')
			if mothername:
				mother = 0
				mother_ids = dog_obj.search(cr,uid,[('name','like',mothername)])
				if mother_ids:
					mother = mother_ids[0]
				else:
					labo_ids = labo_obj.search(cr,uid,[('code','=',row_field(line,'LPFNLB'))])
					if labo_ids:
						mother = dog_obj.create(cr,uid,{'name':row_field(line,'LPFNOM'),
											'progenus_number':row_field(line,'LPFNPR'),
											'origin':row_field(line,'LPFNOR'),
											'tatoo':row_field(line,'LPFTAT'),
											'sex':'f',
											'race':row_field(line,'LPRACE'),
											'birthdate':row_field_date(line,'LPFDTN'),
											'ship':row_field(line,'LPFPUC'),
											'pedigree':row_field(line,'LPFNUM'),
											'labo_id':labo_ids[0]
											})
					else :
						new_labo_f = 0
						if row_field(line,'LPFLLB') and row_field(line,'LPFNLB'):
							new_labo_f=labo_obj.create(cr,uid,{
										'name':row_field(line,'LPFLLB'),
										'ref':row_field(line,'LPFRLB'),
										'code':row_field(line,'LPFNLB'),
										})
						mother = dog_obj.create(cr,uid,{'name':row_field(line,'LPFNOM'),
											'progenus_number':row_field(line,'LPFNPR'),
											'origin':row_field(line,'LPFNOR'),
											'tatoo':row_field(line,'LPFTAT'),
											'sex':'f',
											'race':row_field(line,'LPRACE'),
											'birthdate':row_field_date(line,'LPFDTN'),
											'ship':row_field(line,'LPFPUC'),
											'pedigree':row_field(line,'LPFNUM'),
											'labo_id':new_labo_f,
											})
				fields['dog_mother']=mother

			"""
			Set the Father dog to labo sample
			   'LPMNOM':'dog_father/name',
			   'LPMNUM':'dog_father/pedigree',
			   'LPMTAT':'dog_father/tatoo',
			   'LPMPUC':'dog_father/ship',
			   'LPMNOR':'dog_father/origin',
			   'LPMDTN':'dog_father/birthdate',
			   'LPMRLB':'dog_father/labo_id/ref',
			   'LPMLLB':'dog_father/labo_id/name',
			   'LPMNLB':'dog_father/labo_id/code',
			   'LPMNPR':'dog_father/progenus_number',
			"""
			fathername = row_field(line,'LPMNOM')
			if fathername:
				father = 0
				father_ids = dog_obj.search(cr,uid,[('name','like',fathername)])
				if father_ids:
					father = father_ids[0]
				else:
					labo_ids = labo_obj.search(cr,uid,[('code','=',row_field(line,'LPMNLB'))])
					if labo_ids:
						father = dog_obj.create(cr,uid,{'name':row_field(line,'LPMNOM'),
											'progenus_number':row_field(line,'LPMNPR'),
											'origin':row_field(line,'LPMNOR'),
											'tatoo':row_field(line,'LPMTAT'),
											'sex':'M',
											'race':row_field(line,'LPRACE'),
											'birthdate':row_field_date(line,'LPMDTN'),
											'ship':row_field(line,'LPMPUC'),
											'pedigree':row_field(line,'LPMNUM'),
											'labo_id':labo_ids[0],
											})
					else :
						new_labo_m = 0
						if row_field(line,'LPMLLB') and row_field(line,'LPMNLB'):
							new_labo_m=labo_obj.create(cr,uid,{
										'name':row_field(line,'LPMLLB'),
										'ref':row_field(line,'LPMRLB'),
										'code':row_field(line,'LPMNLB'),
										})
						father = dog_obj.create(cr,uid,{'name':row_field(line,'LPMNOM'),
											'progenus_number':row_field(line,'LPMNPR'),
											'origin':row_field(line,'LPMNOR'),
											'tatoo':row_field(line,'LPMTAT'),
											'sex':'M',
											'race':row_field(line,'LPRACE'),
											'birthdate':row_field_date(line,'LPMDTN'),
											'ship':row_field(line,'LPMPUC'),
											'pedigree':row_field(line,'LPMNUM'),
											'labo_id':new_labo_m,
											})
			fields['dog_father']=father

			"""
			Set the Child dog to labo sample
			   'LPCSEX':'dog_child/sex',
			   'LPCTAT':'dog_child/tatoo',
			   'LPCPUC':'dog_child/ship',
			   'LPCDTN':'dog_child/birthdate',
			   'LPCNPR':'dog_child/progenus_number',
			   'LPRACE':'dog_child/race',
			   'LPSEQ':'dog_child/seq',
			"""
			child_prog_number = row_field(line,'LPCNPR')
			if child_prog_number:
				child = 0
				child_ids = dog_obj.search(cr,uid,[('progenus_number','like',child_prog_number)])
				if child_ids:
					child = child_ids[0]
				else:
					labo_ids = labo_obj.search(cr,uid,[('code','=',1)])
					if labo_ids:
						child = dog_obj.create(cr,uid,{'name':row_field(line,'LPCNPR'),
											'progenus_number':row_field(line,'LPCNPR'),
											#'origin':row_field(line,'LPMNOR'),
											'tatoo':row_field(line,'LPCTAT'),
											'sex':row_field(line,'LPCSEX'),
											'race':row_field(line,'LPRACE'),
											'birthdate':row_field_date(line,'LPCDTN'),
											'ship':row_field(line,'LPCPUC'),
											'seq':row_field(line,'LPSEQ'),
											'labo_id':labo_ids[0],
											'parent_m_id':mother,
											'parent_f_id':father,
											})
					else :
						new_labo_c=labo_obj.create(cr,uid,{
									'name':'Progenus',
									'ref':'1',
									'code':'1',
									})
						child = dog_obj.create(cr,uid,{'name':row_field(line,'LPCNPR'),
											'progenus_number':row_field(line,'LPCNPR'),
											#'origin':row_field(line,'LPMNOR'),
											'tatoo':row_field(line,'LPCTAT'),
											'sex':row_field(line,'LPCSEX'),
											'race':row_field(line,'LPRACE'),
											'birthdate':row_field_date(line,'LPCDTN'),
											'ship':row_field(line,'LPCPUC'),
											'seq':row_field(line,'LPSEQ'),
											'labo_id':new_labo_c,
											'parent_m_id':mother,
											'parent_f_id':father,
											})
			fields['dog_child']=child
			type_id=pooler.get_pool(cr.dbname).get('labo.analysis.type').search(cr, uid,[('code', 'ilike', 'EMPDOG')])
			type_id_s=type_id and type_id[0]
			if row_field(line,'LPNRAP') and flag!=row_field(line,'LPNRAP'):
				res=row_field(line,'LPNRAP').split('/')
				num= ",".join([str(x) for x in res[1:] if x]).replace('"','').replace(',','')
				request_id=req_obj.create(cr,uid,{'type_id':type_id_s, 'name':num})
				flag=row_field(line,'LPNRAP')
			else:
				has_id=req_obj.search(cr,uid,[('type_id','=',type_id_s)])
				request_id=has_id and has_id[0]
				if not len(has_id):
					request_id=pooler.get_pool(cr.dbname).get('labo.analysis.request').create(cr,uid,{'type_id':type_id_s, 'name':'to_set'})
			fields['sample_id']=request_id
			sample_id=sample_obj.create(cr,uid,fields)
	return {}


class import_attach(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'form', 'arch': _form_cont, 'fields': _fields_cont, 'state':[('end','Cancel'), ('done','Import')]}
		},
		'done': {
			'actions': [import_attachment],
			'result': {'type': 'state', 'state':'end'}
		}

	}
import_attach('labo.analysis.xls')
