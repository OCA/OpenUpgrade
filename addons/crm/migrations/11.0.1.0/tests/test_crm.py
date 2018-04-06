# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


class TestCrm(TransactionCase):
    def _check_match(self, cr, record_id):
        """Check that there's a value in the column that links with old record.
        """
        column_name = AsIs(openupgrade.get_legacy_name('crm_activity'))
        cr.execute(
            "SELECT %s FROM mail_activity_type WHERE id = %s",
            (column_name, record_id)
        )
        row = cr.fetchone()
        self.assertTrue(row[0])

    def test_mail_activity_type_standard(self):
        """Check that standard types have been matched"""
        cr = self.env.cr
        xml_ids = [
            'mail.mail_activity_data_email',
            'mail.mail_activity_data_call',
            'mail.mail_activity_data_todo',
        ]
        for xml_id in xml_ids:
            self._check_match(cr, self.env.ref(xml_id).id)

    def test_mail_activity_type_extra(self):
        """Check that custom types have been added"""
        record = self.env['mail.activity.type'].search([
            ('name', '=', 'Follow-up Quote'),
        ])
        self.assertTrue(record)
        self._check_match(self.env.cr, record.id)

    def test_mail_activity(self):
        """Check that mail.activity records are correctly created."""
        lead = self.env.ref('crm.crm_case_13')
        record = self.env['mail.activity'].search([
            ('res_id', '=', lead.id),
            ('res_model', '=', 'crm.lead'),
        ])
        self.assertTrue(record)
        self.assertEquals(
            record.summary, 'Meeting to go over pricing information.',
        )
        self.assertEquals(record.activity_type_id.name, 'Todo')
        self.assertEquals(record.user_id, self.env.ref('base.user_root'))
