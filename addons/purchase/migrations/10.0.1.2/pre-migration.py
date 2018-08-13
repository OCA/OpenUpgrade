# coding: utf-8
# Copyright 2018 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """ Delete the translations of the email templates that are being
    overwritten in the noupdate_changes.xml """
    openupgrade.delete_record_translations(
        env.cr, 'purchase', [
            'email_template_edi_purchase_done',
            'email_template_edi_purchase',
        ])
