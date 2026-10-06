# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup
from openupgradelib import openupgrade


def ir_access_end(env):
    env.cr.execute(
        """
        SELECT DISTINCT
        im.id, im.model
        FROM
        ir_access ia
        JOIN
        ir_model im
        ON
        ia.model_id=im.id
        WHERE
        ia.active
        AND ia.id NOT IN (
            SELECT res_id
            FROM ir_model_data
            WHERE
            model='ir.access'
            AND module NOT IN (
                '__export__', '__custom__'
            )
        )
        """
    )
    custom_access_models = env.cr.fetchall()
    admin_channel = env.ref("mail.channel_admin", raise_if_not_found=False)
    if custom_access_models and admin_channel:
        model_list = ""
        for model_id, model_name in custom_access_models:
            model_list += f'<a href="/odoo/ir.model/{model_id}">{model_name}</a><br/>'
        admin_channel.message_post(
            body=Markup(
                f"""
            <div class="alert alert-warning">Custom record rules and model access</div>
            <p>You have customized your model access rules.
            Note the v19 approach does not map exactly to v20, so you need to
            review and test carefully that the migrated access records for the
            following models do what you expect.</p>
            <p>Be especially cautious with group based restrictions, those will
            most likely not work the way they used to.</p>
            <p>Models with custom access:</p>
            <p>{model_list}</p>
            """
            )
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.disable_invalid_filters(env)
    ir_access_end(env)
