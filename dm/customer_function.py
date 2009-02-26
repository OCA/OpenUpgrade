import pooler
from osv import osv
from osv import fields

__description__ = '''
					This plugin returns the value of the field for customer
				'''
__args__ = []

def customer_function(cr,uid,customer_ids,**args):
	pool = pooler.get_pool(cr.dbname)
	object = args['object']
	dm_customer = pool.get(object)
	if object=='res.partner.address' :
		customer_ids = dm_customer.search(cr,uid,[('partner_id','in',customer_ids)])
	customers = dm_customer.read(cr,uid,customer_ids,[args['field_name']])
	if args['field_type'] == 'char':
		value = map(lambda x : (x['id'],x[args['field_name']]),customers)
	elif args['field_type'] == 'boolean':
		value = map(lambda x : (x['id'],str(x[args['field_name']])),customers)
	elif args['field_type'] == 'many2one':
		for id in customers:
	     		if id[args['field_name']]:
		     		id[args['field_name']] = str(id[args['field_name']][1])
		value = map(lambda x : (x['id'],x[args['field_name']]),customers)
	elif args['field_type'] == 'many2many':
		value=[]
		for id in customers:
			for field_id in id[args['field_name']]:
				browse_id = pool.get(args['field_relation']).browse(cr,uid,[field_id])[0]
				tpl = (id['id'], browse_id.name)
				value.append(tpl)
	elif args['field_type'] == 'selection':
		for id in customers:
			if id[args['field_name']]:
				if args['field_name'] == 'lang':
					res_lang = pool.get('res.lang')
					language = res_lang.search(cr,uid,[('code','=',id[args['field_name']])])
					read_name = res_lang.read(cr,uid,language,['name'])
					id[args['field_name']] = str(read_name[0]['name'])
		value = map(lambda x : (x['id'],x[args['field_name']]),customers)
	print "==================",value
	return value
