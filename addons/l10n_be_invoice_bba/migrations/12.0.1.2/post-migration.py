# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'l10n_be_invoice_bba',
        'migrations/12.0.1.2/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'account', [
            'email_template_edi_invoice',
        ],
    )
