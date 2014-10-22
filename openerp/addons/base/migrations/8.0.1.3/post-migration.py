# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association
#    @author: Sylvain LE GAL <https://twitter.com/legalsylvain>
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

import logging
from openerp import pooler, SUPERUSER_ID
from openerp.openupgrade import openupgrade
logger = logging.getLogger('OpenUpgrade')


def check_ir_actions_server_state(cr, pool):
    """Test if 'state' values are correct.
    If not, log an error to indicate that the user has to overload _get_state
    function in his custom modules."""
    ias_obj = pool['ir.actions.server']
    valid_selection = ias_obj._get_states(cr, SUPERUSER_ID)
    valid_list = [x[0] for x in valid_selection]
    ias_ids = ias_obj.search(
        cr, SUPERUSER_ID, [('state', 'not in', valid_list)])
    for ias in ias_obj.browse(cr, SUPERUSER_ID, ias_ids):
        logger.error(
            "Invalid value '%s' in the model 'ir_actions_server' "
            "for the field 'state'. (id %s).Please overload the new "
            "ir_actions_server._get_state function." % (
                ias.state, ias.id))


def check_commercial_partner(cr, pool):
    """ Test if the column is present (iow: if there exists a partner with a parent"""
    if not openupgrade.column_exists(cr, "res_partner", "commercial_partner_id"):
        sql = """ALTER TABLE res_partner ADD COLUMN commercial_partner_id int"""
        cr.execute(sql)


def remove_account_report_company_record(cr, pool):
    """An ir_ui_view record from the discontinued module account_report_company is not removed and causes an
    AttributeError, remove it here to fix that error. """
    view_obj = pool.get('ir.ui.view')
    view_ids = view_obj.search(cr, SUPERUSER_ID,
                               [('arch', 'like', '//templates//'), ('name', '=', 'res.partner kanban')])
    view_obj.unlink(cr, SUPERUSER_ID, view_ids)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    check_ir_actions_server_state(cr, pool)
    check_commercial_partner(cr, pool)
    remove_account_report_company_record(cr, pool)
