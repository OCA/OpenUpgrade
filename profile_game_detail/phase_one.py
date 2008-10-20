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

from osv import fields, osv
import pooler

class profile_game_detail_phase_one(osv.osv):
    _name="profile.game.detail.phase1"
    _columns = {
        'step1': fields.boolean('Create Quotation'),
        'step1_so_id': fields.many2one('sale.order', 'Quotation / Sale Order'),
        'step2': fields.boolean('Print Customer Quotation'),
        'step3': fields.boolean('Confirm Sale Order'),

        'step4': fields.boolean('Print Request for Quotation'),
        'step6': fields.boolean('Change Supplier Price'),
        'step6': fields.boolean('Confirm Request for Quotation'),

        'step8': fields.boolean('Receive Products from Supplier'),
        'step9': fields.boolean('Deliver Products to Customer'),

        'step9': fields.boolean('Confirm Draft Invoice'),
        'step10': fields.boolean('Print Customer Invoice'),

        'progress': fields.function(_progress, method=True, string='Overall Progress')
        'next_step': fields.function(_next_step, method=True, string='Next Step Explanation')
        'state' fields.selection([
            ('quotation','Create Quotation'),
            ('print_quote','Print Quotation'),
            ('sale','Confirm Sale Order'),
            ('print_rfq','Print Request for Quotation'),
            ('modify_price','Modify Price RfQ'),
            ('confirm_po','Confirm Purchase Order'),
            ('receive','Receive Products'),
            ('deliver','Deliver Products'),
            ('invoice_create','Confirm Invoice'),
            ('invoice_print','Print Invoice'),
        ], 'State', required=True)
    }
    _defaults = {
        'state': lambda *args: 'quotation'
    }
profile_game_detail_phase_one()

