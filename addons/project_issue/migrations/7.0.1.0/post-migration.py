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
    crm_category2project_category = {}
    for category in pool['crm.case.categ'].browse(
            cr, SUPERUSER_ID, category_ids):
        new_category_id = pool['project.category'].create(
            cr, SUPERUSER_ID, {
                'name': category.name,
            })
        crm_category2project_category[category.id] = new_category_id

    cr.execute('alter table crm_case_categ add column %s integer' %
               openupgrade.get_legacy_name('project_category_id'))

    for category_id, new_category_id in crm_category2project_category\
            .iteritems():
        cr.execute(
            'insert into %s (%s, %s) '
            'select id, %%s from project_issue where categ_id=%%s' %
            pool['project.issue']._columns['categ_ids']._sql_names(
                pool['project.issue']),
            (new_category_id, category_id,))
        cr.execute(
            'update crm_case_categ set %s=%%s where id=%%s' %
            openupgrade.get_legacy_name('project_category_id'),
            (new_category_id, category_id))


@openupgrade.migrate()
def migrate(cr, version):
    if not version:
        return
    pool = pooler.get_pool(cr.dbname)
    openupgrade.set_defaults(
        cr, pool, {'project.project': [('use_issues', None)]})
    migrate_categories(cr, pool)
