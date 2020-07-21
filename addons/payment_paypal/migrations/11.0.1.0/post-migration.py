# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _replace_paypal_view_template_id(env):
    """As this view is removed being noupdate=1 (and we don't want to keep it
    as invalid), we need to switch the view for possible records of this
    provider.
    """
    acquirers = env['payment.acquirer'].search([
        ('provider', '=', 'paypal'),
        ('view_template_id', '=', env.ref(
            'payment_paypal.paypal_acquirer_button').id),
    ])
    if not acquirers:
        return
    # Do it through SQL for avoiding other validations
    openupgrade.logged_query(
        env.cr, """
        UPDATE payment_acquirer
        SET view_template_id = %s
        WHERE id IN %s
        """, (
            env.ref('payment_paypal.paypal_form').id,
            tuple(acquirers.ids),
        )
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'payment_paypal', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
    _replace_paypal_view_template_id(env)
