import pooler
from osv import osv
from osv import fields

__description__ = '''
                    This plugin returns the value of the field for customer
                '''
__args__ = []

def customer_function(cr, uid, **args):
    pool = pooler.get_pool(cr.dbname)
    model_name = args['model_name']
    model_object =  pool.get(model_name)
    if model_name in ['dm.workitem','dm.campaign','dm.offer.step','dm.trademark'] and 'wi_id' in args:
        data = pool.get('dm.workitem').browse(cr,uid,args['wi_id'])
        if not data.segment_id : return False
        if not data.segment_id.proposition_id : return False
        if not data.segment_id.proposition_id.camp_id.trademark_id : return False
        if model_name == 'dm.campaign':
            res = pool.get(model_name).read(cr,uid,data.segment_id.proposition_id.camp_id.id)
        elif model_name == 'dm.offer.step':
            res = pool.get(model_name).read(cr,uid,data.step_id.id)
        elif model_name == 'dm.trademark' :
            res = pool.get(model_name).read(cr,uid,data.segment_id.proposition_id.camp_id.trademark_id.id)
        else:
            res = pool.get(model_name).read(cr,uid,args['wi_id'])
    else :
        res = pool.get('res.partner.address').read(cr,uid,args['addr_id'])
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
                res[args['field_name']] = read_name[0]['name']
        value = res[args['field_name']]
        return value
    elif args['field_type'] == 'many2one':
        if res[args['field_name']]:
            if args['field_name'] == 'lang_id':
                if res['lang_id'] :
                    read_name = pool.get('res.lang').read(cr,uid,res['lang_id'][0],['name'])
                    res[args['field_name']] =read_name['name']
                else : return ' '
            elif args['field_name'] == 'country_id' or args['field_name'] == 'country':
                id = 0
                if res['country_id']: 
                    id = res['country_id'][0]
                elif res['country']:
                    id = res['country'][0]
                else : return ' '
                if id != 0:
                    read_name = pool.get('res.country').read(cr,uid,id,['name'])
                    res[args['field_name']] = read_name['name']
            elif args['field_name'] == 'name':
                if res['name']:
                    read_name = pool.get('res.partner').read(cr,uid,res['name'][0],['name'])
                    res[args['field_name']] = read_name['name']
                else : return ' '
        if (model_name == 'dm.workitem'):
            if args['field_name'] == 'tr_from_id':
                if res['tr_from_id']:
                    previous_step_id = pool.get('dm.offer.step.transition').browse(cr,uid,res['tr_from_id'][0])
                    return previous_step_id.step_from_id.id
                else : return False
            else : 
                return res[args['field_name']] and res[args['field_name']][0] or ''
        return res[args['field_name']]
    elif args['field_type'] not in ['many2many','one2many']:
        return res[args['field_name']]
