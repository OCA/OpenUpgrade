# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# This migration script copyright (C) 2015 Therp BV (<http://therp.nl>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID


def migrate_categories(cr, pool):
    category_ids = pool['crm.case.categ'].search(
        cr, SUPERUSER_ID, [('object_id.model', '=', 'project.issue')])
    for category in pool['crm.case.categ'].browse(
            cr, SUPERUSER_ID, category_ids):
        pool['project.category'].create(
            cr, SUPERUSER_ID, {
                'name': category.name,
            })
    pool['crm.case.categ'].unlink(cr, SUPERUSER_ID, category_ids)


@openupgrade.migrate()
def migrate(cr, version):
    if not version:
        return
    pool = pooler.get_pool(cr.dbname)
    openupgrade.set_defaults(
        cr, pool, {'project.project': [('use_issues', None)]})
    migrate_categories(cr, pool)
