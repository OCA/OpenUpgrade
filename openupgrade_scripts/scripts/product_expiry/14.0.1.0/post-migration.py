# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """ UPDATE
                product_template
            SET
                use_expiration_date = 't'
            WHERE
                expiration_time > 0
        """
    )
