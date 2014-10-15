# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association
#    @author: Onestein <www.onestein.nl>
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


def load_data(cr):
    '''
    Update the references to group_portal.
    :param cr:
    '''
    openupgrade.load_data(cr, 'portal', 'portal_data.xml', mode='init')


def migrate_group_users(cr, uid, pool):
    '''
    Migrate groups portal and anonymous
    :param cr: cursor
    '''
    data_obj = pool['ir.model.data']
    old_group_portal = data_obj.get_object_reference(cr, uid, 'portal', 'group_portal')[1]
    new_group_portal = data_obj.get_object_reference(cr, uid, 'base', 'group_portal')[1]
    if old_group_portal and new_group_portal:
        cr.execute("""update res_groups_users_rel set gid=%s where gid=%s""",
                   (new_group_portal, old_group_portal,))
        cr.execute("""DELETE FROM res_groups WHERE id = %s""", (old_group_portal,))

    old_group_anonymous = data_obj.get_object_reference(cr, uid, 'portal', 'group_anonymous')[1]
    new_group_public = data_obj.get_object_reference(cr, uid, 'base', 'group_public')[1]

    if old_group_anonymous and new_group_public:
        cr.execute("""update res_groups_users_rel set gid=%s where gid=%s""",
                   (new_group_public, old_group_anonymous,))
        cr.execute("""DELETE FROM res_groups WHERE id = %s""", (old_group_anonymous,))


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    user = SUPERUSER_ID
    migrate_group_users(cr, user, pool)
    load_data(cr)
