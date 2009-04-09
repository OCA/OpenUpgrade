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

from osv import fields,osv


#######################################
# Connector
#######################################

class magento_web(osv.osv):
    _name = 'magento.web'
    _description = 'Magento Web'
    _columns = {
        'magento_flag'      : fields.boolean('Magento web flag', help="The Magento active web must have this box checked."),
        'magento_name'      : fields.char('Magento web name', size=64),
        'magento_url'       : fields.char('Magento Url', size=64, help="URL to Magento shop ending with /"),
        'api_user'          : fields.char('Magento Api User', size=64),
        'api_pwd'           : fields.char('Magento Api Password', size=64),
        'auto_update'       : fields.boolean('Auto update products and categories', help="If auto update is checked, when you create, modify or delete products and categories in OpenERP, they are automatically created, modified or deleted in Magento. Also, if a existing product or category in OpenERP is checked as exportable, it is created in Magento. And when is unchecked as exportable, it is deleted in Magento."),
    }
    
    def _constraint_unique(self, cr, uid, ids):
        web = self.pool.get('magento.web').search(cr, uid,[])
        if len(web) > 1 :
            return False
        else :
            return True
    
    _constraints = [
        (_constraint_unique, _('Error: The module has been designed for only one Magento Web.'), [])
    ]
    
    # for lack of a better place to put this    
    def createOrders(self, cr, uid, sale_order_array):
        import netsvc
        import magento_utils
        logger = netsvc.Logger()
        logger.notifyChannel(_("Magento Import"), netsvc.LOG_INFO, "createOrders")

        utils = magento_utils.magento_utils()
        results = utils.createOrders(cr, uid, sale_order_array)

        return results
    
    #Magento Connection
    def connect(self, cr, uid, ids, datas = {}, context = {} ):
        import xmlrpclib
        import netsvc
        connect_logger = netsvc.Logger()
        
        try:
            magento_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
            if len(magento_id) > 1 :
                raise osv.except_osv(_('UserError'), _('You must have only one shop with Magento flag turned on'))
            else :
                magento_web = self.pool.get('magento.web').browse(cr, uid, magento_id[0])
                server = xmlrpclib.ServerProxy("%sindex.php/api/xmlrpc" % magento_web.magento_url)
            
        except Exception, error:
            raise osv.except_osv(_("UserError"), _("You must have a declared website with a valid URL, a Magento username and password"))
            connect_logger.notifyChannel(_("Magento Connect"), netsvc.LOG_ERROR, _("Error : %s") % error)
   
        try:
            session = server.login(magento_web.api_user, magento_web.api_pwd)
            
        except xmlrpclib.Fault,error:
            raise osv.except_osv(_("MagentoError"), _("Magento returned %s") % error)
        except Exception, error:
            raise osv.except_osv(_("ConnectionError"), _("Couldn't connect to Magento with URL %sindex.php/api/xmlrpc") % magento_web.magento_url)

        return server, session

    
    #TODO Refactor with connect method
    def connect_custom_api(self, cr, uid, ids, datas = {}, context = {}):
        import xmlrpclib
        import netsvc
        connect_logger = netsvc.Logger()
        
        try:
            magento_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
            if len(magento_id) > 1 :
                raise osv.except_osv(_('UserError'), _('You must have only one shop with Magento flag turned on'))
            else :
                magento_web = self.pool.get('magento.web').browse(cr, uid, magento_id[0])
                server = xmlrpclib.ServerProxy("%sapp/code/local/Smile/OpenERPSync/openerp-synchro.php" % magento_web.magento_url)
            
        except Exception, error:
            raise osv.except_osv(_("UserError"), _("You must have a declared website with a valid URL, a Magento username and password"))
            connect_logger.notifyChannel(_("Magento Connect"), netsvc.LOG_ERROR, _("Error : %s") % error)

        return server

magento_web()
