# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Zikzakmedia S.L. (http://www.zikzakmedia.com) All Rights Reserved.
# @authors: Raphaël Valyi, Jordi Esteve
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

class product_pricelist(osv.osv):
    _inherit = 'product.pricelist'
    _columns = {
        'magento_id': fields.integer('Magento client group id', help="You must create a client group in Magento and put its id in this field. Left 0 if you don't want to synchronize this price list."),
        'magento_default': fields.boolean('Default Magento price list', help="The price list with this box checked will be used to compute the Magento general prices (the standard prices of each product)."),
    }
    _defaults = {
        'magento_id': lambda *a: 0,
    }

product_pricelist()