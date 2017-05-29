# -*- coding: utf-8 -*-
# © 2017 Paul Catinean <https://www.pledra.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def migrate_bom(cr):
    # Multiply line product_efficiency with the parent bom efficiency and store
    # While this method would yield different results if it is run twice
    # because the value is not indempotent migration should either work or
    # roll back changes
    cr.execute("""
        UPDATE mrp_bom_line
        SET product_efficiency = mrp_bom_line.product_efficiency *
                                 mrp_bom.product_efficiency
            FROM mrp_bom
            WHERE mrp_bom_line.bom_id = mrp_bom.id;
        """)


@openupgrade.migrate(use_env=True)
def migrate(env, version):

    cr = env.cr
    migrate_bom(cr)
