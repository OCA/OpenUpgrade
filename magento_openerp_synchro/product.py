from osv import fields,osv

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'magento_id': fields.integer('Magento product id'),
        'exportable': fields.boolean('Export to website'), 
        'updated': fields.boolean('Product updated on Magento'),
        'magento_tax_class_id': fields.integer('Magento tax class Id'),
    }
    _defaults = {
        'magento_id': lambda *a: 0,
        'exportable': lambda *a: True,
        'updated': lambda *a: False,
        'magento_tax_class_id': lambda *a: 2,
    }

    def write(self, cr, uid, ids, datas = {}, context = {} ):
        super(osv.osv, self).write(cr, uid, ids, datas, context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if mw.auto_update :
            datas['model']='product.product'
            datas['ids']=ids
            import wizard.magento_product_synchronize
            wizard.magento_product_synchronize.do_export(self, cr, uid, datas, context)
            del datas['model']
            del datas['ids']
        else :
            self.pool.get('product.product').write(cr, uid, ids, {'updated': False})
        return 1 

    def create(self, cr, uid, datas, context = {}):
        id = super(osv.osv, self).create(cr, uid, datas, context=context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if mw.auto_update :
            datas['model'] = 'product.product'
            datas['ids'] = [id]
            import wizard.magento_product_synchronize
            wizard.magento_product_synchronize.do_export(self, cr, uid, datas, context)
            del datas['model']
            del datas['ids']
        else :
            self.pool.get('product.product').write(cr, uid, [id], {'updated': False})
        return id

    def write_magento_id(self, cr, uid, ids, datas = {}, context = {} ):
        return super(osv.osv, self).write(cr, uid, ids, datas, context)

product_product()


class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
        'magento_id': fields.integer('magento category id'),
        'exportable': fields.boolean('Export to website'),
        'updated': fields.boolean('Category updated on Magento'),
        'magento_product_type': fields.integer('Magento Product Type'), 
        'magento_product_attribute_set_id': fields.integer('Magento Product Attribute Set Id'), 
    }
    _defaults = {
        'magento_id': lambda *a: 0,
        'exportable':lambda *a: True,
        'updated': lambda *a: False,
        'magento_product_type': lambda *a: 0,
        'magento_product_attribute_set_id': lambda *a: 0,
    }

    def write(self, cr, uid, ids, datas = {}, context = {} ):
        super(osv.osv, self).write(cr, uid, ids, datas, context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if mw.auto_update :
            datas['model']='product.category'
            datas['ids']=ids
            import wizard.magento_category_synchronize
            wizard.magento_category_synchronize.do_export(self, cr, uid, datas, context)
            del datas['model']
            del datas['ids']
        else :
            self.pool.get('product.category').write(cr, uid, ids, {'updated': False})
        return 1

    def create(self, cr, uid, datas, context = {}):
        id = super(osv.osv, self).create(cr, uid, datas, context=context)
        mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
        mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
        if mw.auto_update :
            datas['model'] = 'product.category'
            datas['ids'] = [id]
            import wizard.magento_category_synchronize
            wizard.magento_category_synchronize.do_export(self, cr, uid, datas, context)
            del datas['model']
            del datas['ids']
        else :
            self.pool.get('product.category').write(cr, uid, [id], {'updated': False})
        return id

    def write_magento_id(self, cr, uid, ids, datas = {}, context = {} ):
        return super(osv.osv, self).write(cr, uid, ids, datas, context)

product_category()