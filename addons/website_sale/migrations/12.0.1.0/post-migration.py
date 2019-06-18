# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_120
from ast import literal_eval


def update_res_company_website_sale_states(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE res_company
        SET website_sale_onboarding_payment_acquirer_state = 'done'
        """
    )


def fill_website_config_parameters(env):
    # cart_abandoned_delay
    params = env['ir.config_parameter'].sudo()
    cart_abandoned_delay = float(params.get_param(
        'website_sale.cart_abandoned_delay', 1.0))
    openupgrade.logged_query(
        env.cr, """
        UPDATE website
        SET cart_abandoned_delay = %s
        """, (cart_abandoned_delay, ),
    )
    # cart_recovery_mail_template_id
    cart_recovery_mail_template_id = literal_eval(params.get_param(
        'website_sale.cart_recovery_mail_template_id', default='False'))
    if cart_recovery_mail_template_id and not env['mail.template'].browse(
            cart_recovery_mail_template_id).exists():
        ref = env.ref(
            'website_sale.mail_template_sale_cart_recovery',
            raise_if_not_found=False)
        cart_recovery_mail_template_id = ref and ref.id or False
    if cart_recovery_mail_template_id:
        openupgrade.logged_query(
            env.cr, """
            UPDATE website
            SET cart_recovery_mail_template_id = %s
            """, (cart_recovery_mail_template_id, ),
        )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    update_res_company_website_sale_states(cr)
    fill_website_config_parameters(env)
    openupgrade.load_data(
        cr, 'website_sale', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'website_sale', ['mail_template_sale_cart_recovery'],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'website_sale.group_website_multi_image',
        ],
    )
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'product.template', 'website_description',
    )
