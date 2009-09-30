#########################################################################
# Copyright (C) 2009  Sharoon Thomas & Open ERP Community               #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################
from osv import osv,fields

class product_product(osv.osv):
    _inherit = "product.template"
    _columns = {
        'categ_id': fields.many2one('product.category','Pricing/Primary Category', required=True, change_default=True),
        'categ_ids': fields.many2many('product.category','product_categ_rel','product_id','categ_id','Product Categories')
    }
product_product()
