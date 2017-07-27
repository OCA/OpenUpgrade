# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

xmlids_renames = [
    ('sale_portal.email_template_edi_sale',
     'sale.email_template_edi_sale'),
    ('sale_portal.email_template_edi_invoice',
     'account.email_template_edi_invoice'),
]


@openupgrade.migrate()
def migrate(env, version):
    env['ir.model.data'].search([
        ('module', '=', 'sale'),
        ('name', '=', 'email_template_edi_sale'),
    ]).unlink()
    env['ir.model.data'].search([
        ('module', '=', 'account'),
        ('name', '=', 'email_template_edi_invoice'),
    ]).unlink()
    openupgrade.rename_xmlids(env.cr, xmlids_renames)
