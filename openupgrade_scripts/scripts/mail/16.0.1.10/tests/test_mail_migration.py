from datetime import datetime

from odoo.tests import TransactionCase


class TestMailMigration(TransactionCase):
    def test_mail_scheduled_date(self):
        """Make sure that the scheduled date was preserved as changing
        the field type from char to datetime.
        """
        mail_with_date = self.env["mail.mail"].search(
            [("body_html", "=", "TEST date")], limit=1
        )
        self.assertEqual(len(mail_with_date), 1)
        self.assertEqual(
            mail_with_date.scheduled_date,
            datetime(2023, 4, 12, 10, 5, 1),
        )
        mail_without_date = self.env["mail.mail"].search(
            [("body_html", "=", "TEST empty date")], limit=1
        )
        self.assertEqual(len(mail_without_date), 1)
        self.assertFalse(mail_without_date.scheduled_date)
