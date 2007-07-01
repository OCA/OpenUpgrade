import wizard
import osv
from datetime import date
import time
import pooler
import xmlrpclib
import re
import tools

acc_synchro_form = '''<?xml version="1.0"?>
<form string="Transfer Data To Server">
	<field name="server_url" colspan="4"/>
	<newline/>
	<newline/>
</form>'''

acc_synchro_fields = {
	'server_url': {'string':'Server URL', 'type':'many2one', 'relation':'base.synchro.server','required':True},
}

finish_form ='''<?xml version="1.0"?>
<form string="Synchronization Complited!">
	<label string="Data Transfered successfully!!!" colspan="4"/>
</form>
'''

class RPCProxyOne(object):
	def __init__(self, server, ressource):
		self.server = server
		local_url = 'http://%s:%d/xmlrpc/common'%(server.server_url,server.server_port)
		rpc = xmlrpclib.ServerProxy(local_url)
		self.uid = rpc.login(server.server_db, server.login, server.password)
		local_url = 'http://%s:%d/xmlrpc/object'%(server.server_url,server.server_port)
		self.rpc = xmlrpclib.ServerProxy(local_url)
		self.ressource = ressource
	def __getattr__(self, name):
		return lambda cr, uid, *args, **kwargs: self.rpc.execute(self.server.server_db, self.uid, self.server.password, self.ressource, name, *args, **kwargs)

class RPCProxy(object):
	def __init__(self, server):
		self.server = server
	def get(self, ressource):
		return RPCProxyOne(self.server, ressource)

class wizard_cost_account_synchro(wizard.interface):
	def _synchronize(self, cr, uid, server, object, context):
		pool = pooler.get_pool(cr.dbname)
		self.meta = {}
		ids = []
		pool1 = RPCProxy(server)
		pool2 = pool
		if object.action in ('d','b'):
			ids = pool1.get('base.synchro.obj')._get_ids(cr, uid, 
				object.model_id.model, 
				object.synchronize_date, 
				eval(object.domain), 
				{'action':'d'}
			)
		if object.action in ('u','b'):
			ids += pool2.get('base.synchro.obj')._get_ids(cr, uid, 
				object.model_id.model, 
				object.synchronize_date, 
				eval(object.domain), 
				{'action':'u'}
			)
		ids.sort()
		for dt, id, action in ids:
			if action=='u':
				pool_src = pool2
				pool_dest = pool1
			else:
				pool_src = pool1
				pool_dest = pool2
			value = pool_src.get(object.model_id.model).read(cr, uid, [id], context)[0]
			value = self._data_transform(cr, uid, pool_src, object.model_id.model, value, action, context)

			id2 = self.get_id(cr, uid, object.id, id, action, context)
			#
			# Transform value
			#
			if id2:
				pool_dest.get(object.model_id.model).write(cr, uid, [id2], value)
			else:
				idnew = pool_dest.get(object.model_id.model).create(cr, uid, value)
				synid = pool.get('base.synchro.obj.line').create(cr, uid, {
					'obj_id': object.id,
					'local_id': (action=='u') and id or idnew,
					'remote_id': (action=='d') and id or idnew
				})
		self.meta = {}
		return 'finish'

	#
	# IN: object and ID
	# OUT: ID of the remote object computed:
	#        If object is synchronised, read the sync database
	#        Otherwise, use the name_search method
	#
	def get_id(self, cr, uid, object_id, id, action, context={}):
		pool = pooler.get_pool(cr.dbname)
		field_src = (action=='u') and 'local_id' or 'remote_id'
		field_dest = (action=='d') and 'local_id' or 'remote_id'
		rid = pool.get('base.synchro.obj.line').search(cr, uid, [('obj_id','=',object_id), (field_src,'=',id)], context)
		result = False
		if rid:
			result  = pool.get('base.synchro.obj.line').read(cr, uid, rid, [field_dest], context=context)[0][field_dest]
		return result

	def _relation_transform(self, cr, uid, object, id, action, context={}):
		if not id:
			return False
		pool = pooler.get_pool(cr.dbname)
		cr.execute('''select o.id from base_synchro_obj o left join ir_model m on (o.model_id =m.id) where
				m.model=%s and
				o.active''', (object,))
		obj = cr.fetchone()
		result = False
		if obj:
			result = self.get_id(cr, uid, obj[0], id, action, context)
		if not result:
			result = id
		return result

	def _data_transform(self, cr, uid, pool_src, object, data, action='u', context={}):
		self.meta.setdefault(pool_src, {})
		if not object in self.meta[pool_src]:
			self.meta[pool_src][object] = pool_src.get(object).fields_get(cr, uid, context)
		fields = self.meta[pool_src][object]

		for f in fields:
			ftype = fields[f]['type']

			if ftype in ('function', 'one2many', 'one2one'):
				del data[f]
			elif ftype == 'many2one':
				if data[f]:
					data[f] = self._relation_transform(cr, uid, fields[f]['relation'], data[f][0], action, context)
			elif ftype == 'many2many':
				res = map(lambda x: self._relation_transform(cr, uid, fields[f]['relation'], x, action, context), data[f])
				data[f] = [(6, 0, res)]
		del data['id']
		return data

	#
	# Find all objects that are created or modified after the synchronize_date
	# Synchronize these obejcts
	# 
	def _upload_download(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		server = pool.get('base.synchro.server').browse(cr, uid, data['form']['server_url'], context)
		for object in server.obj_ids:
			dt = time.strftime('%Y-%m-%d %H:%M:%S')
			self._synchronize(cr, uid, server, object, context)
			if object.action=='b':
				dt = time.strftime('%Y-%m-%d %H:%M:%S')
			pool.get('base.synchro.obj').write(cr, uid, [object.id], {'synchronize_date': dt})
			cr.commit()
		return 'finish'

	states = {
		'init': {
			'actions': [],
			'result': {'type':'form', 'arch':acc_synchro_form, 'fields':acc_synchro_fields, 'state':[('end','Cancel'),('upload_download','Synchronize')]}
		},
		'upload_download': {
			'actions': [],
			'result':{'type':'choice', 'next_state': _upload_download}
		},
		'finish': {
			'actions': [],
			'result':{'type':'form', 'arch':finish_form,'fields':{},'state':[('end','Ok')]}
		},
	}
wizard_cost_account_synchro('account.analytic.account.transfer')


