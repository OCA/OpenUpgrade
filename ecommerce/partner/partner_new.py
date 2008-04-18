from osv import osv, fields
import pooler

class res_partner_category_ecommerce(osv.osv):
    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context)
        res = []
        for record in reads:
            name = record['name']
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = self.name_get(cr, uid, ids)
        return dict(res)
    
    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from res_partner_category where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

   
    _name = 'res.partner.category.ecommerce'
    _description='Partner Categories for ecommerce'
    _columns = {
        'name': fields.char('Category Name', required=True, size=64),
        'parent_id': fields.many2one('res.partner.category', 'Parent Category', select=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
        'child_ids': fields.one2many('res.partner.category.ecommerce', 'parent_id', 'Childs Category'),
        'active' : fields.boolean('Active'),
                }
    
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]
    _defaults = {
        'active' : lambda *a: 1,
    }
    _order = 'parent_id,name'
    
res_partner_category_ecommerce()


def _lang_get(self, cr, uid, context={}):
    obj = self.pool.get('res.lang')
    ids = obj.search(cr, uid, [])
    res = obj.read(cr, uid, ids, ['code', 'name'], context)
    res = [(r['code'], r['name']) for r in res]
    return res + [(False, '')]

class res_partner_ecommerce(osv.osv):
    _description='Partner Ecommerce'
    _name = "res.partner.ecommerce"
    _order = "name"
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'last_name': fields.char('Last Name', size=128, required=True, select=True),
        'birthdate': fields.date('Birthdate', size=64),
        'gender': fields.selection( [ ('male','Male'),('female','Female')],'Gender'),
        'parent_id': fields.many2one('res.partner.ecommerce','Main Company', select=True),
        'child_ids': fields.one2many('res.partner.ecommerce', 'parent_id', 'Partner Ref.'),
        'lang': fields.selection(_lang_get, 'Language', size=5),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'state_id': fields.many2one("res.country.state", 'State', domain="[('country_id','=',country_id)]"),
        'country_id': fields.many2one('res.country', 'Country'),
        'email': fields.char('E-Mail', size=64),
        'phone': fields.char('Phone', size=64),
        'fax': fields.char('Fax', size=64),
        'mobile': fields.char('Mobile', size=64),
        'active': fields.boolean('Active'),
        'category_id': fields.many2many('res.partner.category', 'res_partner_category_rel', 'partner_id', 'category_id', 'Categories'),
             }
    _defaults = {
        'active': lambda *a: 1,
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the partner must be unique !')
    ]

    def copy(self, cr, uid, id, default=None, context={}):
        name = self.read(cr, uid, [id], ['name'])[0]['name']
        default.update({'name': name+' (copy)'})
        return super(res_partner, self).copy(cr, uid, id, default, context)
    
    def _check_ean_key(self, cr, uid, ids):
        for partner_o in pooler.get_pool(cr.dbname).get('res.partner').read(cr, uid, ids, ['ean13',]):
            thisean=partner_o['ean13']
            
            if thisean and thisean!='':
                if len(thisean)!=13:
                    return False
                sum=0
                
                for i in range(12):
                    if not (i % 2):
                        sum+=int(thisean[i])
                    else:
                        sum+=3*int(thisean[i])
                if math.ceil(sum/10.0)*10-sum!=int(thisean[12]):
                    return False
        return True

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        if context.get('show_ref', False):
            rec_name = 'ref'
        else:
            rec_name = 'name'
            
        res = [(r['id'], r[rec_name]) for r in self.read(cr, uid, ids, [rec_name], context)]
        return res
        
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            ids = self.search(cr, uid, [('ref', '=', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

res_partner_ecommerce()

