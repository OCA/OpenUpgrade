# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def rename_image_attachments(env):
    for old, new in [("image_medium", "image_128")]:
        openupgrade.logged_query(
            env.cr, """
            UPDATE ir_attachment SET res_field = %s
            WHERE res_field = %s AND res_model = 'event.sponsor'""",
            (new, old),
        )


@openupgrade.migrate()
def migrate(env, version):
    rename_image_attachments(env)
