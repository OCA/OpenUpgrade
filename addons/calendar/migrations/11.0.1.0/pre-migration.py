# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Now user_id is required, set it to the one who created the entry
    env.cr.execute(
        """
        UPDATE calendar_contacts SET user_id = create_uid 
        WHERE user_id IS NULL;
        """
    )
