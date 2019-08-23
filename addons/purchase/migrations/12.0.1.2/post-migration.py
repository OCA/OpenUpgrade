# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_purchase_order_user_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE purchase_order
        SET user_id = create_uid
        WHERE user_id IS NULL""",
    )


def reset_context_purchase_actions(env):
    env.ref('purchase.purchase_rfq').context = '{}'
    env.ref('purchase.purchase_form_action').context = '{}'


@openupgrade.migrate()
def migrate(env, version):
    fill_purchase_order_user_id(env.cr)
    reset_context_purchase_actions(env)
    openupgrade.load_data(
        env.cr, 'purchase', 'migrations/12.0.1.2/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'purchase', [
            'email_template_edi_purchase',
            'email_template_edi_purchase_done',
        ],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'purchase.mail_template_data_notification_email_purchase_order',
        ],
    )
