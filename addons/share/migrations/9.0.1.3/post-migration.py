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


def remove_share_module(cr):
    pool = RegistryManager.get(cr.dbname)
    ir_module_module = pool['ir.module.module']
    domain = [('name', '=', 'share'),
              ('state', 'in', ('installed', 'to install', 'to upgrade'))]
    ids = ir_module_module.search(cr, SUPERUSER_ID, domain)
    ir_module_module.module_uninstall(cr, SUPERUSER_ID, ids)


@openupgrade.migrate()
def migrate(cr, version):
    remove_share_module(cr)
