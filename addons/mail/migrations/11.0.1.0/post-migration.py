# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def move_notify_email_to_notification_type_field(env):
    mapping = [
        ('email', 'always'),
        ('inbox', 'none'),
    ]
    for item in mapping:
        openupgrade.logged_query(
            env.cr, """
            UPDATE res_users ru SET notification_type = %s
            FROM res_partner rp
            WHERE ru.partner_id = rp.id
                AND rp.notify_email = %s""", item,
        )


def set_binding_model_id_in_action_window(env):
    env.cr.execute("""
        UPDATE ir_act_window SET binding_model_id = subquery.model_id
        FROM (
            SELECT model_id, ref_ir_act_window
            FROM mail_template WHERE ref_ir_value IS NOT NULL
        ) AS subquery
        WHERE ir_act_window.id = subquery.ref_ir_act_window
    """)


@openupgrade.migrate()
def migrate(env, version):
    move_notify_email_to_notification_type_field(env)
    set_binding_model_id_in_action_window(env)
    openupgrade.load_data(
        env.cr, 'mail', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
