# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association, Microcom
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

import logging
from openupgradelib import openupgrade
logger = logging.getLogger('OpenUpgrade')


def map_base(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('base'),
        'base',
        [('1', 'pricelist'), ('2', 'list_price')],
        table='product_pricelist_item', write='sql')


@openupgrade.migrate()
def migrate(cr, version):
    map_base(cr)
