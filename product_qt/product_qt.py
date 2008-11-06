# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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

from osv import osv, fields
import pooler
import time
import math

from tools import config

#----------------------------------------------------------
# Quality Testing
#----------------------------------------------------------

class quality_test(osv.osv):
    _name = "quality.test"
    _description = "quality testings"
    _columns = {
        'name': fields.char('Test Case', size=256),
        'description': fields.text('Description'),
        }
quality_test()

class testing_result(osv.osv):
    _name ="testing.result"
    _columns = {
        'product' :fields.many2one('product.product', string='Product',readonly=True),
        'test_case':fields.one2many('quality.test.config', 'test_id', 'Cases'),
        'tester': fields.many2one('hr.employee',string='Tested By'),
        'test_date': fields.date('Testing Date'),
        'type':fields.selection([('rw_mat','Raw Material Testing'),('in_prod','During Production Testing'),('finish_prod','Finish Goods Testing')],'Testing Type', readonly=True, select=True),
                }
    _defaults = {
        'test_date':lambda *a: time.strftime('%Y-%m-%d')
                  }
testing_result()

class quality_test_config(osv.osv):
    _name = "quality.test.config"
    _description = "quality test configuration"
    _columns = {
        'name': fields.many2one('quality.test','Test Case',),
        'min_limit': fields.float('Min Limit', help='Minimum Limit of measure'),
        'max_limit': fields.float('Max Limit', help='Maximum Limit of measure'),
        'uom': fields.many2one('product.uom','UOM'),
        'product_idr': fields.many2one('product.product', string='Product'),
        'product_idp': fields.many2one('product.product', string='Product'),
        'product_idf': fields.many2one('product.product', string='Product'),
        'actual_val':fields.float('Actual Value'),
        'state':fields.selection([('accepted','Accepted'),('rejected','Rejected')],'Status', readonly=True, select=True),
        'test_id':fields.many2one('testing.result',string='Test Result')
        }
quality_test_config()


#----------------------------------------------------------
# Product
#----------------------------------------------------------

class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"
    _columns = {
        'raw_m_test': fields.one2many('quality.test.config', 'product_idr', 'Raw material testing', help="Quality Testing configuration for raw material."),
        'production_test': fields.one2many('quality.test.config', 'product_idp', 'During Production testing', help="Quality Testing configuration during production."),
        'finished_test': fields.one2many('quality.test.config', 'product_idf', 'Finished Goods testing', help="Quality Testing configuration for finished goods."),
    }
product_product()

class stock_move(osv.osv):
    _inherit ="stock.move"
    _columns = {
        'qlty_test_accept': fields.boolean('Accepted',readonly=True),
        'qlty_test_reject': fields.boolean('Rejected',readonly=True),
                }
    _defaults = {
        'qlty_test_accept': lambda *a: False,
        'qlty_test_reject': lambda *a: False,
                  }
stock_move()

class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'
    _columns ={
        'qlty_test_accept': fields.boolean('Accepted',readonly=True),
        'qlty_test_reject': fields.boolean('Rejected',readonly=True),
                }
    _defaults = {
        'qlty_test_accept': lambda *a: False,
        'qlty_test_reject': lambda *a: False,
                  }
mrp_production_workcenter_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

