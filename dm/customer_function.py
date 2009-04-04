import pooler
from osv import osv
from osv import fields

__description__ = '''
                    This plugin returns the value of the field for customer
                '''
__args__ = []

def customer_function(cr,uid,ids,**args):
    pool = pooler.get_pool(cr.dbname)
    model_name = args['model_name']
    print model_name
    model_object = pool.get(model_name)
#    if model_name=='res.partner.address' :
#        customer = pool.get('res.partner').browse(cr,uid,ids)[0]
#        ids = model_object.search(cr,uid,[('id','=',customer.dm_contact_id.id)])
    customers = model_object.read(cr,uid,ids,[args['field_name']])[0]
    if args['field_type'] == 'char':
        value = customers[args['field_name']]
    elif args['field_type'] == 'boolean':
        value = customers[args['field_name']]
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
        if customers[args['field_name']]:
            if args['field_name'] == 'lang':
                res_lang = pool.get('res.lang')
                language = res_lang.search(cr,uid,[('code','=',customers[args['field_name']])])
                read_name = res_lang.read(cr,uid,language,['name'])
                customers[args['field_name']] = str(read_name[0]['name'])
        value = customers[args['field_name']]
    return value
