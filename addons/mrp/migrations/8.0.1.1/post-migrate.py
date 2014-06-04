# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
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


def move_fields(cr):
    openupgrade.logged_query(
        """UPDATE product_product
           SET produce_delay=(SELECT pt.%s
           FROM product_template
           WHERE product_template.id=product_product.product_tmpl_id)
    """ % openupgrade.get_legacy_name('produce_delay'))


@openupgrade.migrate()
def migrate(cr, version):
    move_fields(cr)
