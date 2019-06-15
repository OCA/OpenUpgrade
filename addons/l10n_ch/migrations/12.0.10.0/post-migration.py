# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_partner_banck_l10n_ch_postal(env):
    banks = env['res.partner.bank'].search([])
    for bank in banks:
        bank._onchange_set_l10n_ch_postal()


@openupgrade.migrate()
def migrate(env, version):
    fill_partner_banck_l10n_ch_postal(env)
    openupgrade.load_data(
        env.cr, 'l10n_ch', 'migrations/12.0.10.0/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'l10n_ch.transfer_account_id',
            'l10n_ch.fiscal_position_tax_template_11',
            'l10n_ch.fiscal_position_tax_template_12',
            'l10n_ch.fiscal_position_tax_template_16',
            'l10n_ch.fiscal_position_tax_template_18',
            'l10n_ch.fiscal_position_tax_template_7',
            'l10n_ch.fiscal_position_tax_template_8',
            'l10n_ch.tax_group_tva_38',
            'l10n_ch.tax_group_tva_8',
        ],
    )
