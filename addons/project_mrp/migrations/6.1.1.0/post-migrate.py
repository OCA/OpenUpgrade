# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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


def migrate(cr, version):
    """compute project.task's sale_line_id"""
    cr.execute(
        'select t.id, t.project_id, po.sale_id '
        'from project_task t '
        'join procurement_order po on t.procurement_id=po.id '
        'where po.sale_id is not null')
    for task_id, project_id, sale_id in cr.fetchall():
        # we're looking for a sale line with the same project that is not
        # yet claimed. That's the best matching we can do
        cr.execute(
            'update project_task set sale_line_id = '
            '(select l.id from sale_order_line l '
            'join product_product p on l.product_id=p.id '
            'where '
            'not exists (select id from project_task where sale_line_id=l.id) '
            'and l.order_id=%s and p.project_id=%s) where id=%s',
            (sale_id, project_id, task_id))
