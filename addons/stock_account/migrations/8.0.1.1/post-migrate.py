# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID


def create_properties(cr, pool):
    """ Fields moved to properties (cost_method).

    Write using the ORM so the cost_method will be written as properties.
    """
    template_obj = pool['product.template']
    company_obj = pool['res.company']
    company_ids = company_obj.search(cr, SUPERUSER_ID, [])
    sql = ("SELECT id, %s FROM product_template" %
           openupgrade.get_legacy_name('cost_method'))
    cr.execute(sql)
    for template_id, cost_method in cr.fetchall():
        for company_id in company_ids:
            ctx = {'force_company': company_id}
            template_obj.write(cr, SUPERUSER_ID, [template_id],
                               {'cost_method': cost_method},
                               context=ctx)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    create_properties(cr, pool)
