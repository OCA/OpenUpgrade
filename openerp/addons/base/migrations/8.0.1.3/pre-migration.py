# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association
#    @author: Sylvain LE GAL <https://twitter.com/legalsylvain>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.openupgrade import openupgrade
from openerp.addons.openupgrade_records.lib import apriori

xml_ids = [
    ('portal.group_anonymous', 'base.group_public'),
    ('portal.group_portal', 'base.group_portal'),
    ('l10n_gt.GTQ', 'base.GTQ'),
    ('l10n_gt.rateGTQ', 'base.rateGTQ'),
]


def cleanup_modules(cr):
    """Don't report as missing these modules, as they are integrated in
    other modules."""
    openupgrade.update_module_names(
        cr, [
            # from OCA/product-attribute
            ('product_customer_code', 'product_supplierinfo_for_customer'),
            # from OCA/sale-workflow - included in core
            ('sale_multi_picking', 'sale_procurement_group_by_line'),
            # from OCA/stock-logistics-workflow
            ('stock_cancel', 'stock_picking_back2draft'),
        ], merge_modules=True,
    )


@openupgrade.migrate()
def migrate(cr, version):
    # Drop view that inhibits changing field types. It will be recreated BTW
    cr.execute('drop view if exists report_document_user cascade')

    openupgrade.update_module_names(
        cr, apriori.renamed_modules.iteritems()
    )
    openupgrade.rename_xmlids(cr, xml_ids)
    openupgrade.check_values_selection_field(
        cr, 'ir_act_report_xml', 'report_type',
        ['controller', 'pdf', 'qweb-html', 'qweb-pdf', 'sxw', 'webkit'])
    openupgrade.check_values_selection_field(
        cr, 'ir_ui_view', 'type', [
            'calendar', 'diagram', 'form', 'gantt', 'graph', 'kanban',
            'qweb', 'search', 'tree'])
    
    # The tables stock.picking.in and stock.picking.out are merged into 
    # stock.picking
    openupgrade.logged_query(
        cr, """
        UPDATE ir_attachment
        SET res_model = 'stock.picking'
        WHERE res_model in ('stock.picking.in', 'stock.picking.out');
        """)
    
    # Product.template is used for non variant product in v7 this was
    # product.product
    openupgrade.logged_query(
        cr, """
        UPDATE ir_attachment
        SET res_model = 'product.template'
        WHERE res_model = 'product.product';
        """)

    cleanup_modules(cr)
