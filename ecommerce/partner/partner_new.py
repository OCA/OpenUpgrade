# -*- encoding: utf-8 -*-
from osv import osv, fields
import pooler


def _lang_get(self, cr, uid, context={}):
    obj = self.pool.get('res.lang')
    ids = obj.search(cr, uid, [])
    res = obj.read(cr, uid, ids, ['code', 'name'], context)
    res = [(r['code'], r['name']) for r in res]
    return res + [(False, '')]

class ecommerce_partner(osv.osv):
    _description='Partner Ecommerce'
    _name = "ecommerce.partner"
    _order = "name"
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'last_name': fields.char('Last Name', size=128, required=True, select=True),
        'lang': fields.selection(_lang_get, 'Language', size=5),
        'company_name':fields.char('Company Name',size=64),
        'active': fields.boolean('Active'),
        'address': fields.one2many('ecommerce.partner.address', 'partner_id', 'Contacts'),
        'category_ids': fields.many2many('res.partner.category', 'ecommerce_partner_category_rel', 'partner_id', 'category_id', 'Categories'),
    }
    _defaults = {
        'active': lambda *a: 1,
    }
  
    def copy(self, cr, uid, id, default=None, context={}):
        name = self.read(cr, uid, [id], ['name'])[0]['name']
        default.update({'name': name+' (copy)'})
        return super(res_partner, self).copy(cr, uid, id, default, context)
       
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
    
    def address_get(self, cr, uid, ids, adr_pref=['default']):
        cr.execute('select type,id from ecommerce_partner_address where partner_id in ('+','.join(map(str,ids))+')')
        res = cr.fetchall()
        adr = dict(res)
               
        if res:
            default_address = adr.get('default', res[0][1])
        else:
            default_address = False
        result = {}
        for a in adr_pref:
            result[a] = adr.get(a, default_address)
      
        return result
    
    def delivery_grid(self, cr, uid, id , product_list, context={}):
        
        prd_list_ids = []
        res_add = self.pool.get('ecommerce.partner.address')
        delivery_carrier = self.pool.get('delivery.carrier')
        prt_add_id =res_add.search(cr,uid,[('partner_id','in',[id])])
        res_prt_add = res_add.read(cr,uid,prt_add_id,['id','type'],context)
        for tmp_addr_var in res_prt_add:
            if(tmp_addr_var['type'] == 'delivery'):
                address_delivery = tmp_addr_var['type']
                add_id = tmp_addr_var['id']
               
        for prd_ids in product_list:
            prd_list_ids.append(prd_ids[0]) 
       
        deli_carr_ids = delivery_carrier.search(cr,uid,[('product_id','in',prd_list_ids)])
        grid_id = self.grid_get(cr, uid,deli_carr_ids,add_id,{},from_web=True)       
       
        return {'grid_id':grid_id}

    def grid_get(self, cr, uid, ids, contact_id, context={},from_web=False):
        if from_web:
            contact = self.pool.get('ecommerce.partner.address').browse(cr, uid, [contact_id])[0]
            delivery_carrier = self.pool.get('delivery.carrier')
        else:    
            contact = self.pool.get('res.partner.address').browse(cr, uid, [contact_id])[0]
            
        for carrier in self.pool.get('delivery.carrier').browse(cr, uid, ids):
           
            for grid in carrier.grids_id:
                get_id = lambda x: x.id
                country_ids = map(get_id, grid.country_ids)
                state_ids = map(get_id, grid.state_ids)
                if country_ids and not contact.country_id.id in country_ids:
                    continue
                if state_ids and not contact.state_id.id in state_ids:
                    continue
                if grid.zip_from and (contact.zip or '')< grid.zip_from:
                    continue
                if grid.zip_to and (contact.zip or '')> grid.zip_to:
                    continue
                return grid.id
        return False
   
  
ecommerce_partner()

class ecommerce_partner_address(osv.osv):
    _description="Partner Address"
    _rec_name = "username"
    _name="ecommerce.partner.address"
    _columns={
        'username':fields.char('Contact Name',size=128,select=True,required=True),
        'partner_id': fields.many2one('ecommerce.partner', 'Partner', required=True, ondelete='cascade', select=True),
        'type': fields.selection( [ ('default','Default'),('invoice','Invoice'), ('delivery','Delivery'), ('contact','Contact'), ('other','Other') ],'Address Type'),
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
            }

ecommerce_partner_address()



