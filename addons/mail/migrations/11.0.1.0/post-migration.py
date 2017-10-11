# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def move_notify_email_to_notification_type_field(env):
    mapping = [
        ('always', 'email'),
        ('none', 'inbox')
    ]
    for item in mapping:
        env.cr.execute("""
            UPDATE res_users SET notification_type = '%s'
            WHERE id IN (
                SELECT u.id
                FROM res_users u JOIN res_partner p ON u.partner_id = p.id
                WHERE p.notify_email = '%s'
            );
        """ % item)


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
