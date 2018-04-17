# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def cleanup_translations(cr):
    update_templates = (
        'email_template_edi_sale',
        'email_template_edi_invoice',
    )

    openupgrade.delete_record_translations(cr, 'portal_sale', update_templates)


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    cleanup_translations(cr)
