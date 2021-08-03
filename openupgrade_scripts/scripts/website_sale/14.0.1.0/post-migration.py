# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com/>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        """  UPDATE
                            product_template
                        SET
                            website_ribbon_id =
                        (   SELECT
                                product_style_id
                            FROM
                                product_style_product_template_rel
                            WHERE
                                product_template_id=product_template.id
                            ORDER BY id DESC
                            LIMIT 1)
                   """
    )
