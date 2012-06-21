# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__

column_renames = {
    # this is a mapping per table from old column name
    # to new column name, e.g.
    #
    'mail_message': [
        ('name', 'subject'),
        ('message', 'body_text'),
        ],
    }

table_renames = [
    ('mailgate_thread', 'mail_thread'),
    ('mailgate_message', 'mail_message'),
    ]

model_renames = [
    ('mailgate.message', 'mail.message'),
    ]

def migrate(cr, version):
    if not version:
        return
    try:
        logger.info("%s called", me)
        if openupgrade.table_exists(cr, 'mailgate_thread'):
            openupgrade.rename_tables(cr, table_renames)
            openupgrade.rename_columns(cr, column_renames)
            openupgrade.rename_models(cr, model_renames)
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
