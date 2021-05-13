# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from . import models
from odoo import api, SUPERUSER_ID


def _post_init_hook(cr, registry):
    """Recalculate street fields now the countries have their street format set"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    partners = env['res.partner'].with_context(active_test=False).search([])
    for field in ['street_name', 'street_number', 'street_number2']:
        partners._recompute_todo(partners._fields[field])
    partners.recompute()
