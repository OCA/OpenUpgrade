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
    model_object =  pool.get(model_name)
    res = pool.get('res.partner.address').read(cr,uid,ids)[0]
    if model_name =='res.partner' :
        ids  = res['partner_id'][0]
        res = model_object.read(cr,uid,[ids])[0]
   # else :
#        defin res over  here or wuill get an erro
    if args['field_type'] == 'selection':
        if res[args['field_name']]:
            if args['field_name'] == 'lang':
                res_lang = pool.get('res.lang')
                language = res_lang.search(cr,uid,[('code','=',customers[args['field_name']])])
                read_name = res_lang.read(cr,uid,language,['name'])
                customers[args['field_name']] = str(read_name[0]['name'])
        value = customers[args['field_name']]
        return value
    elif args['field_type'] not in ['many2many','one2many','many2one']:
        return res[args['field_name']]
