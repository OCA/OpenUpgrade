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
    if model_name == 'dm.workitem' and 'wi_id' in args:
        res = pool.get(model_name).read(cr,uid,args['wi_id'])
    else :
        res = pool.get('res.partner.address').read(cr,uid,ids)[0]
        if model_name == 'res.partner' :
            if res['partner_id']:
                res = model_object.read(cr,uid,res['partner_id'][0])
        elif model_name in ['res.partner.contact','res.partner.job'] :
            if res['job_id']:
                id = res['job_id']
                if model_name == 'res.partner.contact' : 
                    id = pool.get('res.partner.job').read(cr,uid,id[0])['contact_id']
                res = model_object.read(cr,uid,id[0])
    if args['field_type'] == 'selection':
        if res[args['field_name']]:
            if args['field_name'] == 'lang':
                res_lang = pool.get('res.lang')
                language = res_lang.search(cr,uid,[('code','=',res[args['field_name']])])
                read_name = res_lang.read(cr,uid,language,['name'])
                res[args['field_name']] = str(read_name[0]['name'])
        value = res[args['field_name']]
        return value
    elif args['field_type'] == 'many2one':
        print "args['field_name']", args['field_name'], res
        if res[args['field_name']]:
            if args['field_name'] == 'lang_id':
                read_name = pool.get('res.lang').read(cr,uid,res['lang_id'][0],['name'])
                res[args['field_name']] = str(read_name['name'])
            elif args['field_name'] == 'country_id' or args['field_name'] == 'country':
                id = res['country_id'][0] or res['country'][0]
                read_name = pool.get('res.country').read(cr,uid,id,['name'])
                res[args['field_name']] = str(read_name['name'])
            elif args['field_name'] == 'name':
                read_name = pool.get('res.partner').read(cr,uid,res['name'][0],['name'])
                res[args['field_name']] = str(read_name['name'])
        if args['field_name'].find('id')>=0 :
            return res[args['field_name']][0]
        return res[args['field_name']]
    elif args['field_type'] not in ['many2many','one2many']:
        return res[args['field_name']]
