# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# @authors: Sylvain Pamart, Rapha�l Valyi
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



#===============================================================================
#    Information Form & Fields
#===============================================================================

_export_done_form = '''<?xml version="1.0"?>
<form string="Categories Synchronization">
    <separator string="Categories exported" colspan="4" />
    <field name="categ_new"/>
    <field name="categ_update"/>
</form>'''

_export_done_fields = {
    'categ_new': {'string':'New Categories', 'readonly': True, 'type':'integer'},
    'categ_update': {'string':'Updated Categories', 'readonly': True, 'type':'integer'},
}


def do_export(self, cr, uid, data, context):
    
    #===============================================================================
    #  Init
    #===============================================================================
    categ_new = 0
    categ_update = 0
    logger = netsvc.Logger()
    pool = pooler.get_pool(cr.dbname)
    
     
    if data['model'] == 'ir.ui.menu':
        categ_ids = pool.get('product.category').search(cr, uid, [('exportable','=',True)])
    else:
        categ_ids=[]
        categ_not=[]
        for id in data['ids']:
            exportable_category=pool.get('product.category').search(cr, uid, [('id','=',id),('exportable','=',True)]) 
            if len(exportable_category)==1: categ_ids.append(exportable_category[0])
            else : categ_not.append(id)   
            
        if len(categ_not) > 0: raise wizard.except_wizard("Error", "you asked to export non-exportable categories : IDs %s" % categ_not)

    
    #===============================================================================
    #  Server communication
    #===============================================================================
    magento_web_id=pool.get('magento.web').search(cr,uid,[('magento_id','=',1)])
    try:
        magento_web=pool.get('magento.web').browse(cr,uid,magento_web_id[0])
        server = xmlrpclib.ServerProxy("%sindex.php/api/xmlrpc" % magento_web.magento_url)   
    except:
        raise wizard.except_wizard("UserError", "You must have a declared website with a valid URL, a Magento username and password")
    try:
        try:
            session=server.login(magento_web.api_user, magento_web.api_pwd)
        except xmlrpclib.Fault,error:
            raise wizard.except_wizard("MagentoError", "Magento returned %s" % error)
    except:
        raise wizard.except_wizard("ConnectionError", "Couldn't connect to Magento with URL %sindex.php/api/xmlrpc" % magento_web.magento_url)
    
    #===============================================================================
    #  Category packaging
    #===============================================================================
    for category in pool.get('product.category').browse(cr, uid, categ_ids, context=context):
    
        path=''             #construct path
        magento_parent_id=1 #root catalog
        if(type(category.parent_id.id)== (int)): #if not root category
            
            last_parent=pool.get('product.category').browse(cr, uid, category.parent_id.id)
            magento_parent_id=last_parent.magento_id
            path= str(last_parent.magento_id)
            
            while(type(last_parent.parent_id.id) == (int)):
                
                last_parent=pool.get('product.category').browse(cr, uid, last_parent.parent_id.id)
                path=str(last_parent.magento_id)+'/'+path
                
        path='1/'+path
        path=path.replace("//","/")
        if path.endswith('/'): 
            path=path[0:-1]
        
        category_data={
                'name' : category.name,
                'path' : path,
                'is_active' : 1,
        }
        
        #===============================================================================
        #  Category upload to Magento
        #===============================================================================
        
        try:
            if(category.magento_id == 0):
                new_id=server.call(session,'category.create',[magento_parent_id, category_data])
                pool.get('product.category').write_magento_id(cr, uid, category.id, {'magento_id': new_id})
                categ_new += 1
                
            else:
                category_data['path']=category_data['path']+"/"+str(category.magento_id)
                server.call(session,'category.update',[category.magento_id, category_data])
                categ_update += 1
            
                
        except xmlrpclib.Fault,error:
            logger.notifyChannel("Magento Export", netsvc.LOG_ERROR, "Magento API return an error on category id %s . Error %s" % (category.id,error))   

    server.endSession(session)        
    
    return {'categ_new':categ_new, 'categ_update':categ_update }



#===============================================================================
#   Wizard Declaration
#===============================================================================

class wiz_magento_category_synchronize(wizard.interface):
    states = {
        'init': {
            'actions': [do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wiz_magento_category_synchronize('magento.categories.sync');
