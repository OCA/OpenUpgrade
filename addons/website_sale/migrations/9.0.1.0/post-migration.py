# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Vicent Cubells
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openupgradelib import openupgrade_90

attachment_fields = {
    'product.public.category': [
        ('image', None),
        ('image_medium', None),
        ('image_small', None),
    ],
}


def set_last_sale_on_partner(cr):
    openupgrade.logged_query(cr, """
            UPDATE res_partner rp
            SET last_website_so_id = so.id
            FROM sale_order so
            WHERE so.id = (
               SELECT max(id) FROM sale_order
               WHERE partner_id = rp.id
            )
            AND rp.last_website_so_id IS NULL;
            """)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    set_last_sale_on_partner(env.cr)
    openupgrade_90.convert_binary_field_to_attachment(env, attachment_fields)
    openupgrade.load_data(
        env.cr, 'website_sale', 'migrations/9.0.1.0/noupdate_changes.xml',
    )
