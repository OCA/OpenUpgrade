# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_invoices_to_moves(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_analytic_line aal
        SET timesheet_invoice_id = am.id
        FROM account_move am
        WHERE aal.{} = am.old_invoice_id
        """.format(openupgrade.get_legacy_name('timesheet_invoice_id')),
    )


def map_mail_notification_type(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('service_tracking'),
        'service_tracking',
        [('task_new_project', 'task_in_project'),
         ],
        table='product_template',
    )


@openupgrade.migrate()
def migrate(env, version):
    map_invoices_to_moves(env)
    map_mail_notification_type(env)
