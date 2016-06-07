# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute(
        '''update product_template set
        membership = p.membership,
        membership_date_from = p.membership_date_from,
        membership_date_to = p.membership_date_to
        from product_product p
        where p.product_tmpl_id = product_template.id''')
