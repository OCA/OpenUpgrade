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

import pooler, logging
from openerp import SUPERUSER_ID
from openerp.tools.safe_eval import safe_eval
from openerp.openupgrade import openupgrade

def update_actions(cr, pool):
    """
    Update act windows that trigger an email form action. The template id
    is encloded differently in the action's context and the name and view_id of the
    wizard has changed as well.
    """
    cr.execute("""
        SELECT id, context FROM ir_act_window
        WHERE res_model = 'email_template.send.wizard'
    """)
    data_pool = pool.get('ir.model.data')
    view_id = data_pool.get_object_reference(
        cr, SUPERUSER_ID, 'mail', 'email_compose_message_wizard_form')[1]
    for row in cr.fetchall():
        try:
            old_context = safe_eval(row[1] or {}, {'active_id': False, 'active_ids': False})
            if old_context.get('template_id'):
                new_context = (
                    "{'mail.compose.message.mode':'mass_mail', "
                    "'mail.compose.template_id' : %s}" % (old_context['template_id']))
                openupgrade.logged_query(cr, """
                    UPDATE ir_act_window
                    SET res_model = %s,
                        view_id = %s,
                        context = %s
                    WHERE id = %s
                """, ('mail.compose.message', view_id, new_context, row[0]))
        except NameError, e:
            logger = logging.getLogger('OpenUpgrade')
            logger.warn('Could not evaluate %s: %s', old_context, e)

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    update_actions(cr, pool)
