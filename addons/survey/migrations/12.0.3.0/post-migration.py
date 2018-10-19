# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.load_data(
        cr, 'survey', 'migrations/12.0.3.0/noupdate_changes.xml',
    )
    openupgrade.delete_record_translations(
        cr, 'survey', [
            'email_template_survey',
        ],
    )
