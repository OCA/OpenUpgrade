# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012 Therp BV (<http://therp.nl>)
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
from openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade: product')

renamed_columns = {
    'product_supplierinfo': [
        ('qty', 'min_qty')]
    }

def update_packaging_type(cr):
    """ A spelling error has been fixed
    in the selection list """
    cr.execute("""
        UPDATE product_ul
        SET type = %s
        WHERE type = %s""", ('pallet', 'palet'))

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, renamed_columns)
    update_packaging_type(cr)
    logger.warn(
        "TODO: check whether product_packaging.name "
        "preserves content when migrating from type char "
        "to type text")
