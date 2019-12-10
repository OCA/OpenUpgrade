# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    group_public = env.ref('base.group_public')
    partners = group_public.users.mapped('partner_id') | env['website'].search(
        []).mapped('partner_id')
    openupgrade.logged_query(
        env.cr, """DELETE from product_wishlist WHERE session IS NOT NULL AND
                   (partner_id IS NULL OR partner_id in %s)""",
        (tuple(partners.ids),)
    )
