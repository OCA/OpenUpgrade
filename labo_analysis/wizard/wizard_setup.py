
	# -*- coding: iso-8859-1 -*-
##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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
import netsvc

import pooler
from tools.misc import UpdateableStr
from report import report_sxw
#
#def _search(self,cr, uid, datas,context):
#	sample_obj = pooler.get_pool(cr.dbname).get('labo.sample')
#	sample_id=sample_obj.browse(cr,uid,datas['ids'])
#	lst1=[]
#	for i in sample_id:
#	#	setup_ids1=pooler.get_pool(cr.dbname).get('analysis.setup').search(cr,uid,([('sample_id1','=',i.id),('well','>=',97)]))
#		setup_ids1=pooler.get_pool(cr.dbname).get('analysis.setup').search(cr,uid,([('id','=',i.follow_sheet_id.id),('well','>=',97)]))
#		lst1.append(setup_ids1)
#		print "LIST1111111 FROM SEARCH FUNCTION",lst1
#	if len( ",".join(([str(i) for i in lst1 if i])) )>0:
#		print "IN THE SEARCH FN IF STATE"
#		return 'valid2'
#	else:
#		print "IN THE SEARCH FN ELSE STATE"
#		return  'end_print'
#

#def _get_value(self,cr, uid, datas,context):
#	sample_obj = pooler.get_pool(cr.dbname).get('labo.sample')
#	sample_id=sample_obj.browse(cr,uid,datas['ids'])
#	lst=[]
#	print "SAMPLE_IDS:************",sample_id
#	for i in sample_id:
#		print "FOLLOWSHIT_ID",i.follow_sheet_id.id
#		#	setup_ids=pooler.get_pool(cr.dbname).get('analysis.setup').search(cr,uid,([('sample_id1','=',i.id),('well','<',97)]))
#		print "SAMPLE_IDS:************",id
#		print "CURRENT ID",i
#		setup_ids=pooler.get_pool(cr.dbname).get('analysis.setup').search(cr,uid,[('id','=',i.follow_sheet_id.id),('well','<',97)])
#		lst.append(setup_ids)
#		print "LISTTT",lst
#	if not len(lst):
#		print "IN THE GET VALUE IF STATE"
#		return 'valid'
#	else:
#		 print "IN THE GET VALUE ELSE STATE"
#		 return 'valid1'
##	if len(lst):
##		return 'valid1'
##	else: return 'valid'
#
#class wizard_print(wizard.interface):
#	states = {
#		'init': {
#			'actions': [],
#			'result': {'type':'choice',  'next_state':_get_value}
#		},
#		'valid1': {
#			'actions': [],
#			'result': {'type':'print', 'report':'setup', 'state':'valid'}
#		},
#		'valid': {
#			'actions': [],
#			'result': {'type':'choice',  'next_state':_search}
#		},
#		'valid2': {
#			'actions': [],
#			'result': {'type':'print', 'report':'setup1', 'state':'end_print'}
#		},
#
#		'end_print': {
#			'actions': [],
#			'result':{'type':'action', 'action':void_function, 'state':'end'}
#		}
#
#	}
#wizard_print('labo.sample.print')

#CHANGES END AT NEL
# CHANGES START BY PMO



def _search(self,cr, uid, datas,context):

	return False

def void_function(self,cr, uid, datas,context):
	return {}

#
def _sample_partition(self,cr, uid, datas,context):
	global sample_report1
	global sample_report2
	sample_report1= []
	sample_report2= []
	sample_obj = pooler.get_pool(cr.dbname).get('labo.sample')
	sample_id=sample_obj.browse(cr,uid,datas['ids'])
	for i in sample_id:
		if i.file_setup:
			if i.file_setup.well in range(1,97):
				sample_report1.append(i.id)
			elif i.file_setup.well in range(97,193):
				sample_report2.append(i.id)
		else:
			pass
	return {}

def _check_sample_report1(self,cr,uid,datas,context):
	if sample_report1:
		return 'print_sample_report1'
	return 'check_sample_report2'

def check_sample_report2(self,cr,uid,datas,context):
	if sample_report2:
		return 'print_sample_report2'
	return 'end_print'

def _get_samples1(self,cr,uid,datas,context):

	return {'ids': sample_report1}



def _get_samples2(self,cr,uid,datas,context):

	return {'ids': sample_report2}


class wizard_print(wizard.interface):
	states = {
		'init': {
			'actions': [_sample_partition],
			'result': {'type':'action', 'action':void_function, 'state':'check_sample_report1'}
		},
		'check_sample_report1': {
			'actions': [],
			'result': {'type':'choice',  'next_state':_check_sample_report1}
		},
		'check_sample_report2': {
			'actions': [],
			'result': {'type':'choice',  'next_state':check_sample_report2}
		},
		'print_sample_report1': {
			'actions': [_get_samples1],
			'result': {'type':'print', 'report':'setup','get_id_from_action':True, 'state':'check_sample_report2'}
		},
		'print_sample_report2': {
			'actions': [_get_samples2],
			'result': {'type':'print', 'report':'setup1','get_id_from_action':True, 'state':'end_print'}
		},
		'end_print': {
			'actions': [],
			'result':{'type':'action', 'action':void_function, 'state':'end'}
		}

	}
wizard_print('labo.sample.print')

