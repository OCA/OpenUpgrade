from osv import fields , osv                                                       
import datetime
import time
import netsvc
import ir

class ecommerce_shop(osv.osv):
        
    _name = "ecommerce.shop"
    _description = "Shop Basic Info"
    _columns = {
        'name': fields.char('Name', size=256),
        'company_id': fields.many2one('res.company', 'Company'),
        'shop_id': fields.many2one('sale.shop', 'Sale Shop'),     
        'display_search_keyword':fields.boolean('Display  Quick Search'),
        'display_category_cnt': fields.boolean('Display Category Count'),
        'price_with_tax': fields.boolean('Price with Tax'),
        'tell_to_friend': fields.boolean('Tell To Friend'),
        'display_cart': fields.boolean('Display Cart After Shopping'),
        'display_product_name_new': fields.boolean('Display Product Name'),
        'display_manufacturer_name_new': fields.boolean('Display Manufacturer Name'),
        'display_product_image': fields.boolean('Display Product Image'),
        'display_product_price': fields.boolean('Display Product Price'),
        'display_product_quantity': fields.boolean('Display Product Quantity'),
        'display_product_weight': fields.boolean('Display Product Weight'),
        'display_partner_logo':fields.boolean('Display Partner Logo'),
        'display_category_context':fields.boolean('Require Category Context'),
        'display_page_offset':fields.boolean('Require Page Offset'),
        'category_ids': fields.one2many('ecommerce.category', 'web_id','Categories'),
        'products':fields.many2many('product.product','ecommerce_new_product_rel','product','ecommerce_product','Products',readonly=True),
     
    }   
ecommerce_shop()

class ecommerce_category(osv.osv):
       def create(self,cr,uid,vals,context=None):
           
            w_id = vals['web_id']
            if 'category_id' in vals and vals['category_id']:
                cat_id = vals['category_id']
                    
                obj = self.pool.get('product.product').search(cr, uid, [('categ_id','=',cat_id)])
                obj_prd = self.pool.get('product.product').read(cr,uid,obj,[], context={})
                temp=[]
                for i in obj_prd:
                    temp+=[i['id']]
                    
                rec = self.pool.get('ecommerce.shop').write(cr,uid,w_id,{'products':[(6,0,temp)]})
            result = super(osv.osv, self).create(cr, uid, vals, context)
            return result
       
       def write(self,cr,uid,ids,vals,context=None):
            
            obj=self.browse(cr,uid,ids[0])
            curr_id =self.pool.get('ecommerce.shop').browse(cr, uid, ids,context=context)
            web_id = obj.web_id.id
         
            if web_id:
                if 'category_id' in vals and vals['category_id']:
                        cat_id = vals['category_id']
                        obj = self.pool.get('product.product').search(cr, uid, [('categ_id','=',cat_id)])
                        obj_prd = self.pool.get('product.product').read(cr,uid,obj,[], context={})
                        temp=[]
                        for i in obj_prd:
                            temp+=[i['id']]
                        rec = self.pool.get('ecommerce.shop').write(cr,uid,[web_id],{'products':[(6,0,temp)]})
                
            return super(ecommerce_category,self).write(cr,uid,ids,vals,context)
  
       _name = "ecommerce.category"
       _description = "ecommerce category"
       _columns = {
            'name': fields.char('E-commerce Category', size=64, required=True),
            'web_id': fields.many2one('ecommerce.shop', 'Webshop'),
            'category_id': fields.many2one('product.category', 'Tiny Category'),
            'include_childs': fields.boolean('Include Childs'),
            'parent_category_id':fields.many2one('ecommerce.category','Parent Category'),
            'child_id': fields.one2many('ecommerce.category', 'parent_category_id', string='Childs Categories'),        
    }
ecommerce_category()

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'category_image': fields.binary('Category Image')
    }

product_category()