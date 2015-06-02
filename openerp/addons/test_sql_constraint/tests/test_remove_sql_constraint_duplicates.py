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

from openerp.tests import common
from openupgrade.openupgrade import remove_sql_constraint_duplicates


class TestSqlConstraint(common.TransactionCase):
    """
    This Class tests the remove_sql_constraint_duplicates function
    in OpenUpgrade
    """
    def setUp(self):
        super(TestSqlConstraint, self).setUp()
        self.model_1_obj = self.registry('test_sql_contraint.model_1')

        self.user_model = self.registry("res.users")
        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        self.model_1_ids = [
            self.model_1_obj.create(cr, uid, {
                'test_1_a': record[0],
                'test_1_b': record[1],
                'test_1_c': record[2],
            }, context=context) for record in [
                # 11 objects
                (1, 1, 1), (1, 1, 1),
                (1, 1, 2),

                (1, 2, 1), (1, 2, 1), (1, 2, 1),

                (2, 2, 2),
                (2, 2, 3), (2, 2, 3),

                (3, 3, 3), (3, 3, 3),
            ]
        ]

    def get_model_1_records(self):
        cr, uid, context = self.cr, self.uid, self.context

        ids = self.model_1_obj.search(cr, uid, [], context=context)

        return self.model_1_obj.browse(cr, uid, ids, context=context)

    def test_remove_duplicates_1_field(self):
        """Test remove_sql_constraint_duplicates with a constraint
        over 1 field"""
        remove_sql_constraint_duplicates(
            self.cr, 'test_sql_contraint.model_1', ['test_1_a'])

        res = self.get_model_1_records()

        self.assertEqual(len(res), 3)

    def test_remove_duplicates_2_fields(self):
        """Test remove_sql_constraint_duplicates with a constraint
        over 1 field"""
        remove_sql_constraint_duplicates(
            self.cr, 'test_sql_contraint.model_1', ['test_1_a', 'test_1_b'])

        res = self.get_model_1_records()

        self.assertEqual(len(res), 4)

    def test_remove_duplicates_3_fields(self):
        """Test remove_sql_constraint_duplicates with a constraint
        over 1 field"""
        remove_sql_constraint_duplicates(
            self.cr, 'test_sql_contraint.model_1', [
                'test_1_a', 'test_1_b', 'test_1_c'])

        res = self.get_model_1_records()

        self.assertEqual(len(res), 6)

    def create_model_2(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.model_2_obj = self.registry('test_sql_contraint.model_2')

        self.model_2_ids = [
            self.model_2_obj.create(cr, uid, {
                'model_1_ids': [(6, 0, [
                    self.model_1_ids[x] for x in record[0]
                ])]
            }, context=context)
            for record in [
                ([0], ),
                ([1], ),
                ([0, 2], ),
                ([1, 2], ),
                ([0, 2, 3, 6, 7, 9], ),
                ([3, 4, 5], ),
            ]
        ]

    def test_remove_duplicates_3_fields_m2m(self):
        """
            Test remove_sql_constraint_duplicates with a constraint
            over 3 fields and objects related to the duplicates
            with a m2m relation
        """
        self.create_model_2()

        remove_sql_constraint_duplicates(
            self.cr, 'test_sql_contraint.model_1',
            ['test_1_a', 'test_1_b', 'test_1_c'])

        res = self.get_model_1_records()
        self.assertEqual(len(res), 6)

        cr, uid, context = self.cr, self.uid, self.context
        records = self.model_2_obj.browse(
            cr, uid, self.model_2_ids, context=context)

        rec_0 = records[0]
        self.assertEqual(len(rec_0.model_1_ids), 1)

        rec_1 = records[1]
        self.assertEqual(len(rec_1.model_1_ids), 1)

        self.assertEqual(rec_0.model_1_ids[0], rec_1.model_1_ids[0])

        rec_2 = records[2]
        self.assertEqual(len(rec_2.model_1_ids), 2)

        self.assertIn(rec_0.model_1_ids[0], rec_2.model_1_ids)

        rec_3 = records[3]
        self.assertEqual(len(rec_3.model_1_ids), 2)

        self.assertIn(rec_0.model_1_ids[0], rec_3.model_1_ids)

        rec_4 = records[4]
        self.assertEqual(len(rec_4.model_1_ids), 6)

        rec_5 = records[5]
        self.assertEqual(len(rec_5.model_1_ids), 1)

        self.assertIn(rec_5.model_1_ids[0], rec_4.model_1_ids)

    def test_remove_duplicates_1_field_m2m(self):
        """
            Test remove_sql_constraint_duplicates with a constraint
            over 1 field and objects related to the duplicates
            with a m2m relation
        """
        self.create_model_2()

        remove_sql_constraint_duplicates(
            self.cr, 'test_sql_contraint.model_1', ['test_1_a'])

        res = self.get_model_1_records()
        self.assertEqual(len(res), 3)

        cr, uid, context = self.cr, self.uid, self.context
        records = self.model_2_obj.browse(
            cr, uid, self.model_2_ids, context=context)

        rec_4 = records[4]
        self.assertEqual(len(rec_4.model_1_ids), 3)

        rec_5 = records[5]
        self.assertEqual(len(rec_5.model_1_ids), 1)

        self.assertIn(rec_5.model_1_ids[0], rec_4.model_1_ids)

    def create_model_3(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.model_3_obj = self.registry('test_sql_contraint.model_3')

        self.model_3_ids = [
            self.model_3_obj.create(cr, uid, {
                'model_1_id': self.model_1_ids[record[0]],
            }, context=context)
            for record in [
                (0, ), (1, ), (2, ), (3, ),
                (4, ), (5, ), (6, ), (7, ),
                (8, ), (9, ), (10, )
            ]
        ]

        self.model_3_ids.append(
            self.model_3_obj.create(cr, uid, {
                'model_1_id': False,
            }, context=context))

    def has_same_model_1_id(self, records):
        self.assertTrue(records[0].model_1_id)
        for record in records:
            self.assertEqual(records[0].model_1_id, record.model_1_id)

    def test_remove_duplicates_3_fields_m2o(self):
        """
            Test remove_sql_constraint_duplicates with a constraint
            over 3 fields and objects related to the duplicates
            with a m2o relation
        """
        cr, uid, context = self.cr, self.uid, self.context

        self.create_model_3()

        remove_sql_constraint_duplicates(
            self.cr, 'test_sql_contraint.model_1',
            ['test_1_a', 'test_1_b', 'test_1_c'])

        res = self.get_model_1_records()
        self.assertEqual(len(res), 6)

        records = self.model_3_obj.browse(
            cr, uid, self.model_3_ids, context=context)

        self.has_same_model_1_id(records[0:2])
        self.has_same_model_1_id(records[2:3])
        self.has_same_model_1_id(records[3:6])
        self.has_same_model_1_id(records[6:7])
        self.has_same_model_1_id(records[7:9])
        self.has_same_model_1_id(records[9:11])

        self.assertFalse(records[11].model_1_id, False)

    def test_remove_duplicates_1_field_m2o(self):
        """
            Test remove_sql_constraint_duplicates with a constraint
            over 1 field and objects related to the duplicates
            with a m2o relation
        """
        cr, uid, context = self.cr, self.uid, self.context

        self.create_model_3()

        remove_sql_constraint_duplicates(
            self.cr, 'test_sql_contraint.model_1', ['test_1_a'])

        res = self.get_model_1_records()
        self.assertEqual(len(res), 3)

        records = self.model_3_obj.browse(
            cr, uid, self.model_3_ids, context=context)

        self.has_same_model_1_id(records[0:6])
        self.has_same_model_1_id(records[6:9])
        self.has_same_model_1_id(records[9:11])

        self.assertFalse(records[11].model_1_id, False)
