# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# @authors: Sylvain Pamart, Raphaël Valyi
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import pooler
import xmlrpclib
import netsvc


def do_export(self, cr, uid, data, context):
    
    categ_new = 0
    categ_update = 0
    categ_fail = 0 
    
    logger = netsvc.Logger()
    self.pool = pooler.get_pool(cr.dbname)
    categ_pool = self.pool.get('product.category')
    
    mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
    mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
    (server, session) = mw.connect()
    
    #===============================================================================
    #  Getting ids
    #===============================================================================
     
    if data['model'] == 'ir.ui.menu':
        categ_ids = categ_pool.search(cr, uid, [('exportable', '=', True)])
    else:
        categ_ids=[]
        categ_not=[]
        for id in data['ids']:
            exportable_category = categ_pool.search(cr, uid, [('id', '=', id), ('exportable', '=', True)]) 
            if len(exportable_category) == 1:
                categ_ids.append(exportable_category[0])
            else:
                categ_not.append(id)
            
        if len(categ_not) > 0:
            raise wizard.except_wizard("Error", "you asked to export non-exportable categories : IDs %s" % categ_not)

    #===============================================================================
    #  Category packaging
    #===============================================================================
    categories = categ_pool.browse(cr, uid, categ_ids, context=context)
    categories.sort(lambda x, y : (int(x.parent_id) or 0) - int(y.parent_id))

    for category in categories :
    
        path=''             #construct path
        magento_parent_id=1 #root catalog
        if(type(category.parent_id.id) == (int)): #if not root category
            
            last_parent=categ_pool.browse(cr, uid, category.parent_id.id)
            magento_parent_id=last_parent.magento_id
            path= str(last_parent.magento_id)
            
            while(type(last_parent.parent_id.id) == (int)):
                
                last_parent=categ_pool.browse(cr, uid, last_parent.parent_id.id)
                path=str(last_parent.magento_id)+'/'+path
                
        path='1/'+path
        path=path.replace("//","/")
        if path.endswith('/'): 
            path=path[0:-1]
        
        category_data = {
                'name' : category.name,
                'path' : path,
                'is_active' : 1,
        }

        #===============================================================================
        #  Category upload to Magento
        #===============================================================================
        
        try:
            if(category.magento_id == 0):
                new_id = server.call(session,'category.create', [magento_parent_id, category_data])
                categ_pool.write_magento_id(cr, uid, category.id, {'magento_id': new_id})
                logger.notifyChannel("Magento Export", netsvc.LOG_INFO, " Successfully created category with OpenERP id %s and Magento id %s" % (category.id, new_id))
                categ_new += 1
                
            else:
                server.call(session,'category.update',[category_magento_id, category_data])
                logger.notifyChannel("Magento Export", netsvc.LOG_INFO, " Successfully updated category with OpenERP id %s and Magento id %s" % (category.id, category.magento_id))
                categ_update += 1
                
        except xmlrpclib.Fault, error:
            if error.faultCode == 102: #turns out that the category doesn't exist in Magento (might have been deleted), try to create a new one.
                try:
                    new_id = server.call(session,'category.create', [magento_parent_id, category_data])
                    categ_pool.write_magento_id(cr, uid, category.id, {'magento_id': new_id})
                    logger.notifyChannel("Magento Export", netsvc.LOG_INFO, " Successfully created category with OpenERP id %s and Magento id %s" % (category.id, new_id))
                    categ_new += 1
                    
                except xmlrpclib.Fault, error:
                    logger.notifyChannel("Magento Export", netsvc.LOG_ERROR, "Magento API return an error on category id %s . Error %s" % (category.id, error))
                    categ_fail += 1    
            else:
                logger.notifyChannel("Magento Export", netsvc.LOG_ERROR, "Magento API return an error on category id %s . Error %s" % (category.id, error))   
                categ_fail += 1 
                
        except Exception, error:
                raise wizard.except_wizard("OpenERP Error", "An error occured : %s " % error)   

    server.endSession(session)        
    
    return {'categ_new':categ_new, 'categ_update':categ_update, 'categ_fail':categ_fail }



#===============================================================================
#   Wizard Declaration
#===============================================================================

_export_done_form = '''<?xml version="1.0"?>
<form string="Categories Synchronization">
    <separator string="Categories exported" colspan="4" />
    <field name="categ_new"/>
    <field name="categ_update"/>
    <field name="categ_fail" />
</form>'''

_export_done_fields = {
    'categ_new': {'string':'New Categories', 'readonly': True, 'type':'integer'},
    'categ_update': {'string':'Updated Categories', 'readonly': True, 'type':'integer'},
    'categ_fail': {'string':'Failed to export Categories', 'readonly': True, 'type':'integer'},
}

class wiz_magento_category_synchronize(wizard.interface):
    states = {
        'init': {
            'actions': [do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wiz_magento_category_synchronize('magento.categories.sync');
