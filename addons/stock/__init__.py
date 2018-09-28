# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import controllers
import models
import report
import wizard


from odoo import api, SUPERUSER_ID


# TODO: Apply proper fix & remove in master
def pre_init_hook(cr):
    # OpenUpgrade: don't uninstall data as this breaks the analysis
    # Origin of this code is https://github.com/odoo/odoo/issues/22243
    return
    # /Openupgrade

    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.model.data'].search([
        ('model', 'like', '%stock%'),
        ('module', '=', 'stock')
    ]).unlink()
