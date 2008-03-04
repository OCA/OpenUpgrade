# -*- coding :utf-8 -*-

from osv import osv, fields
import time, pooler, copy
import ir
class audittrail_rule(osv.osv):
	_name = 'audittrail.rule'
	_columns = {
		"name": fields.char("Rule Name", size=32, required=True),
		"object_id": fields.many2one('ir.model', 'Object', required=True),
		"user_id": fields.many2many('res.users', 'audittail_rules_users', 'user_id', 'rule_id', 'Users'),
		"log_read": fields.boolean("Log reads"),
		"log_write": fields.boolean("Log writes"),
		"log_unlink": fields.boolean("Log deletes"),
		"log_create": fields.boolean("Log creates"),
		"state": fields.selection((("draft", "Draft"),("subscribed", "Subscribed")), "State", required=True),
		"action_id":fields.many2one('ir.actions.act_window',"Action ID"),
	}

	_defaults = {
		'state': lambda *a: 'draft',
		'log_create': lambda *a: 1,
		'log_unlink': lambda *a: 1,
		'log_write': lambda *a: 1,
	}
	__functions = {}

	def subscribe(self, cr, uid, ids, *args):
		for thisrule in self.browse(cr, uid, ids):
			obj = self.pool.get(thisrule.object_id.model)
			if not obj:
				print ("%s WARNING:audittrail:%s is not part of the pool -- change audittrail depends -- setting rule: %s as DRAFT" % (time.strftime('%a, %d %b %Y %H:%M:%S'), thisrule.object_id.model, thisrule.name))
				self.write(cr, uid, ids, {"state": "draft"})
				return False
			for field in ('read','write','create','unlink'):
				if getattr(thisrule, 'log_'+field):
					# backup corresponding method
					self.__functions.setdefault(thisrule.id, [])
					self.__functions[thisrule.id].append( (obj, field, getattr(obj,field)) )
					uids_to_log = []
					for user in thisrule.user_id:
						uids_to_log.append(user.id)
					# override it with the logging variant
					setattr(obj, field, self.logging_fct(getattr(obj,field), thisrule.object_id, uids_to_log))
		val={
			 "name":'View Log',
			 "res_model":'audittrail.log',
			 "src_model":thisrule.object_id.model,
			 "domain":"[('res_id', '=', active_id)]"

		}
		id=self.pool.get('ir.actions.act_window').create(cr, uid, val)
		self.write(cr, uid, ids, {"state": "subscribed","action_id":id})
		val_val={
				 "name":'View Log',
				 "model":thisrule.object_id.model,
				 "key2":"client_action_relate",
				 "value":"ir.actions.act_window"+','+str(id),
				 "object":True,
				 }
		keyword = 'client_action_relate'
		value = 'ir.actions.act_window,'+str(id)
		res = ir.ir_set(cr, uid, 'action', keyword, 'View_log_'+thisrule.object_id.model, [thisrule.object_id.model], value, replace=True, isobject=True, meta=None)
		return True


	def logging_fct(self, fct_src, object, logged_uids):

		if object.model=="audittrail.log":
			return fct_src

		def my_fct( cr, uid, *args, **args2):

			if fct_src.__name__ in ('create'):
				res_id =fct_src( cr, uid, *args, **args2)
				new_value=self.pool.get(object.model).read(cr,uid,[res_id],args[0].keys())[0]
				if new_value:
					if not len(logged_uids) or uid in logged_uids:
						id=self.pool.get('audittrail.log').create(cr, uid, {"method": fct_src.__name__, "object_id": object.id, "user_id": uid, "res_id": res_id,"name": "%s %s %s" % (fct_src.__name__, object.id, time.strftime("%Y-%m-%d %H:%M:%S"))})
						for field in args[0]:
							if new_value[field]:
								f_id= self.pool.get('ir.model.fields').search(cr, uid,[('name','=',field),('model_id','=',object.id)])
								fields=self.pool.get('ir.model.fields').read(cr, uid,f_id)
								if fields[0]['ttype']== 'many2one':
									if new_value[field]:
										new_value[field]=new_value[field][0]
								self.pool.get('audittrail.log.line').create(cr, uid, {"log_id": id, "field_id": f_id[0] ,"old_value":'' ,"new_value":new_value[field],"field_description":fields[0]['field_description']})

				return res_id

			if fct_src.__name__ in ('write'):
				res_ids=args[0]
				for res_id in res_ids:
					old_values=self.pool.get(object.model).read(cr,uid,res_id,args[1].keys())
					res =fct_src( cr, uid, *args, **args2)
					if res:
						new_values=self.pool.get(object.model).read(cr,uid,res_ids,args[1].keys())[0]
						if not len(logged_uids) or uid in logged_uids:
							id=self.pool.get('audittrail.log').create(cr, uid, {"method": fct_src.__name__, "object_id": object.id, "user_id": uid, "res_id": res_id,"name": "%s %s %s" % (fct_src.__name__, object.id, time.strftime("%Y-%m-%d %H:%M:%S"))})
							for field in args[1]:
								f_id= self.pool.get('ir.model.fields').search(cr, uid,[('name','=',field),('model_id','=',object.id)])
								fields=self.pool.get('ir.model.fields').read(cr, uid,f_id)
								old_value=old_values[field]
								new_value=new_values[field]

								if fields[0]['ttype']=='many2one':
									old_value=old_values[field][0]
									new_value=new_values[field][0]

								self.pool.get('audittrail.log.line').create(cr, uid, {"log_id": id, "field_id": f_id[0] ,"old_value":old_value ,"new_value":new_value,"field_description":fields[0]['field_description']})
					return res

			if fct_src.__name__ in ('read'):
				res_ids=args[0]
				old_values={}
				res =fct_src( cr, uid,*args, **args2)
				if type(res)==list:
					for v in res:
						old_values[v['id']]=v
				else:
					old_values[res['id']]=res
				for res_id in old_values:
					if not len(logged_uids) or uid in logged_uids:
						id=self.pool.get('audittrail.log').create(cr, uid, {"method": fct_src.__name__, "object_id": object.id, "user_id": uid, "res_id": res_id,"name": "%s %s %s" % (fct_src.__name__, object.id, time.strftime("%Y-%m-%d %H:%M:%S"))})
						for field in old_values[res_id].keys():
							if old_values[res_id][field]:
								f_id= self.pool.get('ir.model.fields').search(cr, uid,[('name','=',field),('model_id','=',object.id)])
								if len(f_id):
									fields=self.pool.get('ir.model.fields').read(cr, uid,f_id)
									if fields[0]['ttype']== 'many2one':
										old_value=old_values[res_id][field]
									else:
										old_value=old_values[res_id][field]
										self.pool.get('audittrail.log.line').create(cr, uid, {"log_id": id, "field_id": f_id[0] ,"old_value":old_value ,"new_value":'',"field_description":fields[0]['field_description']})
				return res


			if fct_src.__name__ in ('unlink'):
				res_ids=args[0]
				old_values={}
				for res_id in res_ids:
					old_values[res_id]=self.pool.get(object.model).read(cr,uid,res_id,[])

				#if res:
				for res_id in res_ids:
					if not len(logged_uids) or uid in logged_uids:
						id=self.pool.get('audittrail.log').create(cr, uid, {"method": fct_src.__name__, "object_id": object.id, "user_id": uid, "res_id": res_id,"name": "%s %s %s" % (fct_src.__name__, object.id, time.strftime("%Y-%m-%d %H:%M:%S"))})
						for field in old_values[res_id]:
							if old_values[res_id][field]:
								f_id= self.pool.get('ir.model.fields').search(cr, uid,[('name','=',field),('model_id','=',object.id)])
								if f_id:
									fields=self.pool.get('ir.model.fields').read(cr, uid,f_id)
									if fields[0]['ttype']== 'many2one':
										old_value=old_values[res_id][field][0]
									else:
										old_value=old_values[res_id][field]
										self.pool.get('audittrail.log.line').create(cr, uid, {"log_id": id, "field_id": f_id[0] ,"old_value":old_value ,"new_value":'',"field_description":fields[0]['field_description']})
				res =fct_src( cr, uid,*args, **args2)
				return res

		return my_fct

	def unsubscribe(self, cr, uid, ids, *args):
		for thisrule in self.browse(cr, uid, ids):
			if thisrule.id in self.__functions :
				for function in self.__functions[thisrule.id]:
					setattr(function[0], function[1], function[2])
		w_id=self.pool.get('ir.actions.act_window').search(cr, uid, [('name','=','View Log'),('res_model','=','audittrail.log'),('src_model','=',thisrule.object_id.model)])
		self.pool.get('ir.actions.act_window').unlink(cr, uid,w_id )
		if len(w_id):
			val_obj=self.pool.get('ir.values')
			value="ir.actions.act_window"+','+str(w_id[0])
			val_id=val_obj.search(cr, uid, [('model','=',thisrule.object_id.model),('value','=',value)])
			res = ir.ir_del(cr, uid, val_id[0])
		self.write(cr, uid, ids, {"state": "draft"})
		return True

audittrail_rule()


class audittrail_log(osv.osv):
	_name = 'audittrail.log'
	_columns = {
		"name": fields.char("Name", size=32),
		"object_id": fields.many2one('ir.model', 'Object'),
		"user_id": fields.many2one('res.users', 'User'),
		"method": fields.selection((('read', 'Read'), ('write', 'Write'), ('unlink', 'Delete'), ('create', 'Create')), "Method"),
		"timestamp": fields.datetime("Timestamp"),
		"res_id":fields.integer('Resource Id'),
		"line_ids":fields.one2many('audittrail.log.line','log_id','Log lines')

	}
	_defaults = {
		"timestamp": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S")
	}

audittrail_log()

class audittrail_log_line(osv.osv):
	def create(self, cr, uid, vals, context={}):
		field=self.pool.get('ir.model.fields').read(cr, uid,vals['field_id'])
		model=field['relation']
		old_values=vals['old_value']
		new_values=vals['new_value']
		if field['ttype']=='many2one':
			if old_values:
				val=self.pool.get(model).read(cr,uid,[old_values],['name'])
				if len(val):
					vals['old_value_text']=val[0]['name']

			new_id=new_values
			if new_id:
				val=self.pool.get(model).read(cr,uid,[new_id],['name'])
				if len(val):
					vals['new_value_text']=val[0]['name']

		elif field['ttype'] == 'many2many':
			value=[]
			if old_values:
				old_ids=old_values
				for old_id in old_ids:
					val=self.pool.get(model).read(cr,uid,[old_id],['name'])
					if len(val):
						value.append(val[0]['name'])
						vals['old_value_text']=value

			new_ids=new_values
			value=[]
			for new_id in new_ids:
				val=self.pool.get(model).read(cr,uid,[new_id],['name'])
				if len(val):
					value.append(val[0]['name'])
					vals['new_value_text']=value

		elif field['ttype'] == 'one2many':
			value=[]
			if old_values:
				old_ids=old_values
				for old_id in old_ids:
					val=self.pool.get(model).read(cr,uid,[old_id],['name'])
					if len(val):
						value.append(val[0]['name'])
						vals['old_value_text']=value

			if new_values:
				new_ids=new_values
				value=[]
				for new_id in new_ids:
					val=self.pool.get(model).read(cr,uid,[new_id],['name'])
					if len(val):
						value.append(val[0]['name'])
						vals['new_value_text']=value

		elif type =='selection':
			vals['old_value_text']=val[0]['name']
			vals['new_value_text']=val[0]['name']

		else:

			vals['old_value_text']=old_values
			vals['new_value_text']=new_values

		result = super(audittrail_log_line, self).create(cr, uid, vals, context)
		return result

	_name='audittrail.log.line'
	_columns={
			  #"name": fields.char("Name", size=32),
			  'field_id': fields.many2one('ir.model.fields','Fields', required=True),
			  'log_id':fields.many2one('audittrail.log','Log'),
			  'log':fields.integer("Log ID"),
			  'old_value':fields.text("Old Value"),
			  'new_value':fields.text("New Value"),
			  'old_value_text':fields.text('Old value Text' ),
			  'new_value_text':fields.text('New value Text' ),
			  'field_description':fields.char('Field Description' ,size=64),
			  }

audittrail_log_line()