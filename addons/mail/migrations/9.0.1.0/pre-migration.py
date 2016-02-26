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

from openupgradelib import openupgrade
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID

# must be a tuple to output as valid SQL
shared_xmlids = (
	'action_email_template_tree_all',
	# need to migrate changes to those mail.template
	# 'email_template_form',
	# 'email_template_partner',
	# 'email_template_preview_form',
	# 'email_template_tree',
	'menu_email_templates',
	'res_partner_opt_out_search',
	'view_email_template_search',
	'view_server_action_form_template',
	'wizard_email_template_preview',
	)


def update_xmlids(cr):
    openupgrade.logged_query(cr, """
        update ir_model_data set module='mail'
        where name in {0}
        and module = 'email_template'
        """.format(shared_xmlids))
    openupgrade.logged_query(cr, """
        update ir_model_data set model='mail.template'
        where model = 'email.template'
        """)


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_tables(cr, [('email_template', 'mail_template')])
    update_xmlids(cr)
