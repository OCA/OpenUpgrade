# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def recover_old_data_for_admin(env):
    partner_id = env.ref('base.partner_root').id
    env.cr.execute(
        """
        UPDATE res_partner
        SET name, email, image = temporal_name, temporal_email, temporal_image
        WHERE id = %s""", (partner_id, ),
    )
    env.cr.execute(
        """ALTER TABLE res_partner DROP COLUMN IF EXISTS temporal_name""")
    env.cr.execute(
        """ALTER TABLE res_partner DROP COLUMN IF EXISTS temporal_email""")
    env.cr.execute(
        """ALTER TABLE res_partner DROP COLUMN IF EXISTS temporal_image""")


@openupgrade.migrate()
def migrate(env, version):
    recover_old_data_for_admin(env)
