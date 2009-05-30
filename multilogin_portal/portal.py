#!/usr/bin/python2.4
# -*- coding: utf-8 -*-

###___________________________________________________________###
#                                                               #
#	Please edit [OPENERP_PATH]/bin/netsvc.py                     #
#		replace:                                                  #
#			r=m(*params)                                           #
#		by:                                                       #
#			if n=='computer': r=m(self.client_address[0], *params) #
#			else: r=m(*params)                                     #
#		to transmit IP address to log in method                   #
#                                                               #
###___________________________________________________________###

###___________ WEB SERVICES: partner & computer
import netsvc, sql_db

class partner_interface(netsvc.Service):
	def __init__(self,name="partner"):
		netsvc.Service.__init__(self,name)
		self.external_users= {}
		self.joinGroup("web-services")
		self.exportMethod(self.login)
		self.exportMethod(self.execute)
		self.exportMethod(self.exec_workflow)
		self.exportMethod(self.obj_list)
	def login(self, dbname, email, passwd):
		cr= sql_db.db_connect(dbname).cursor()
		cr.execute("""SELECT p.id
		FROM res_partner p, res_partner_address a
		WHERE a.partner_id=p.id AND a.email='%s' AND p.pasword='%s'
		LIMIT 1""" % (email, passwd))
		try: ret= cr.fetchone()[0]
		except: ret= False
		cr.close()
		return ret
	def grant(self, dbname, partner_id, passwd, type):
		if not type in ("provider","customer"): raise 'AccessDenied'
		cr= sql_db.db_connect(dbname).cursor()
		sql= ''
		if type=="provider":
			sql= " AND id IN (SELECT name FROM product_supplierinfo GROUP BY 1)"
		cr.execute("""SELECT password='%s'%s FROM res_partner WHERE id=%d""" % (passwd, sql, partner_id))
		if not cr.rowcount: raise 'AccessDenied'
		if not cr.fetchone()[0]: raise 'AccessDenied'
		if not self.external_users:
			cr.execute("""SELECT user_computer, user_customer, user_provider FROM res_company LIMIT 1""")
			self.external_users= cr.dictfetchone()
		cr.close()
		return self.external_users["user_%s" % type]
	def execute(self, dbname, partner_id, passwd, type, object, method, *args):
		uid=  self.grant(dbname, partner_id, passwd, type)
		return netsvc.LocalService("object").execute(dbname, uid, object, method, *args)
	def exec_workflow(self, dbname, partner_id, passwd, type, object, method, id):
		uid=  self.grant(dbname, partner_id, passwd, type)
		return service.exec_workflow(dbname, uid, object, method, id)
	def obj_list(self, dbname, partner_id, passwd, type):
		uid=  self.grant(dbname, partner_id, passwd, type)
		return service.obj_list()
partner_interface()

class computer_interface(netsvc.Service):
	def __init__(self,name="computer"):
		netsvc.Service.__init__(self,name)
		self.joinGroup("web-services")
		self.external_users= {}
		self.exportMethod(self.execute)
		self.exportMethod(self.exec_workflow)
		self.exportMethod(self.obj_list)
	def grant(self, ip_address, dbname):
		cr= sql_db.db_connect(dbname).cursor()
		cr.execute("""SELECT id FROM res_computer WHERE ip_address='%s'""" % ip_address)
		if not cr.rowcount: raise 'AccessDenied'
		if not self.external_users:
			cr.execute("""SELECT user_computer, user_customer, user_provider FROM res_company LIMIT 1""")
			self.external_users= cr.dictfetchone()
		cr.close()
		return self.external_users["user_computer"]
	def execute(self, ip_address, dbname, object, method, *args):
		uid=  self.grant(ip_address, dbname)
		return netsvc.LocalService("object_proxy").execute(dbname, uid, object, method, *args)
	def exec_workflow(self, ip_address, dbname, object, method, id):
		uid=  self.grant(ip_address, dbname)
		return service.exec_workflow(dbname, uid, object, method, id)
	def obj_list(self, ip_address, dbname):
		uid=  self.grant(ip_address, dbname)
		return service.obj_list()
computer_interface()



###___________ OBJECTS
from osv import fields, osv
import re

class res_company(osv.osv):
	_name = "res.company"
	_inherit = "res.company"
	_columns = {
		'user_provider': fields.many2one('res.users','Providers'),
		'user_customer': fields.many2one('res.users','Customers'),
		'user_computer': fields.many2one('res.users','Computers'),
		}
	def write(self, cr, uid, ids, vals, context={}):
		super(res_company,self).write(cr, uid, ids, vals, context=context)
		cr.commit()
		cr.execute("""SELECT user_computer, user_customer, user_provider FROM res_company LIMIT 1""")
		external_users= cr.dictfetchone()
		netsvc.LocalService("computer").external_users= external_users
		netsvc.LocalService("partner").external_users= external_users
		return True
res_company()

class res_computer(osv.osv):
	_name = "res.computer"
	_description = "Computers"
	_columns = {
		'name': fields.char('Name', size=128,required=True),
		'ip_address': fields.char('IP address', size=15,required=True),
		'state': fields.selection([('online','On line'),('offline','Off line')], 'State',required=True),
		'active': fields.boolean("Active")
		}
	_defaults= {
		'active': lambda *a: True,
		'state': lambda *a: 'offline'
	}
	_sql_constraints= [ ('name_uniq','unique(name)','This name allready exists'), ('ip_uniq','unique(ip_address)','This IP address allready exists') ]
	def _check_ip(self, cr, uid, ids, context={}):
		res= self.browse(cr, uid, ids, context)
		for r in res:
			ok= (re.match(r"([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})", r.ip_address)) and True or False
			if not ok: return False
		return True
	_constraints= [ (_check_ip, 'Please set a real IP address', []) ]
res_computer()
