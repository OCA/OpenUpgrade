# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2014 ONESTEiN B.V.
# Many thanks to: Priit Laes, Povi Software LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.openupgrade import openupgrade

column_renames = {
    'mrp_bom': [
        ('bom_id', None),
        ('product_uos', None),
        ('product_uos_qty', None)
    ],
    'mrp_bom_line': [],
    'mrp_production': [
        ('picking_id', None),
    ],
}


table_spec = [
    ('mrp_bom_property_rel', 'mrp_bom_mrp_property_rel')
]

xmlid_renames = [
    ('procurement.access_mrp_property', 'mrp.access_mrp_property'),
    ('procurement.access_mrp_property_group', 'mrp.access_mrp_property_group'),
]


def drop_report_mrp_view(cr):
    openupgrade.logged_query(cr, "DROP VIEW report_mrp_inout")


def check_production_state(cr):
    """Check if a record with a state that is no longer supported (picking_except)
    exists in mrp_production and adjust it (to draft).
    """
    if not openupgrade.check_values_selection_field(
        cr, 'mrp_production', 'state', ['cancel', 'confirmed', 'done', 'draft', 'in_production', 'ready']
    ):
        # Set picking_except to draft
        sql = """SELECT id FROM mrp_production WHERE state = 'picking_except'"""
        cr.execute(sql)

        prod_ids = tuple([x for x, in tuple(cr.fetchall())])

        sql = """UPDATE mrp_production SET state = 'draft' WHERE id in {}""".format(prod_ids)
        cr.execute(sql)
        cr.commit()


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    drop_report_mrp_view(cr)
    openupgrade.rename_tables(cr, table_spec)
    check_production_state(cr)
    openupgrade.rename_xmlids(cr, xmlid_renames)
