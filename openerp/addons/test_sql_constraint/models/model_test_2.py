# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 OpenUpgrade Community All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import orm, fields


class ModelTest2(orm.Model):
    _name = 'test_sql_contraint.model_2'

    _description = 'Model Test 2'

    _columns = {
        'model_1_ids': fields.many2many(
            'test_sql_contraint.model_1',
            'test_models_1_2_rel',
            'model_2_id',
            'model_1_id',
            'Field 2 B'
        ),
    }
