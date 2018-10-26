# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'mail_mass_mailing_contact': [
        ('opt_out', None),
        ('unsubscription_date', None),
    ],
}


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_columns(cr, _column_renames)
