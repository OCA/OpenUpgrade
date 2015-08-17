# -*- encoding: utf-8 -*-
##############################################################################
#
#    'Point Of Sale' migration module for Odoo
#    copyright: 2014-Today GRAP
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

column_renames = {
    'pos_config': [
        ('shop_id', None),
        ],
    'product_product': [
        ('available_in_pos', None),
        ('expense_pdt', None),
        ('income_pdt', None),
        ('pos_categ_id', None),
        ('to_weight', None),
    ],
}


@openupgrade.migrate(no_version=True)
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
