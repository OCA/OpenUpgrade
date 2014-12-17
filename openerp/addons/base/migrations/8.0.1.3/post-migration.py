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


def remove_account_report_company_record(cr, pool):
    """An ir_ui_view record from the discontinued module """
    """account_report_company is not removed and causes an
    AttributeError, remove it here to fix that error. """
    view_obj = pool['ir.ui.view']
    try:
        view_id = pool['ir.model.data'].get_object_reference(
            cr, SUPERUSER_ID, 'account_report_company',
            'account_report_copmany_partner_kanban_view')[1]
        view_obj.unlink(cr, SUPERUSER_ID, [view_id])
    except ValueError:
        pass


def ensure_admin_email(cr, pool):
    """During migration, there are writes via the ORM to tracking
    fields. This breaks if admin neither has a valid alias nor an email"""
    admin = pool['res.users'].browse(cr, SUPERUSER_ID, SUPERUSER_ID)
    if not admin.email and not pool['ir.config_parameter'].get_param(
            cr, SUPERUSER_ID, 'mail.catchall.domain'):
        # that's the default value for new installations
        default_email = 'info@example.com'
        openupgrade.message(
            'base', None, None,
            'No email address for admin and no catchall domain defined - '
            'setting admin\'s email address to %s', default_email)
        admin.write({'email': default_email})


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    check_ir_actions_server_state(cr, pool)
    remove_account_report_company_record(cr, pool)
    ensure_admin_email(cr, pool)
