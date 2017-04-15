# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestMail(TransactionCase):
    def test_mail(self):
        # check that our test mails have the correct states
        notification = self.env['mail.notification'].search([
            (
                'mail_message_id', '=',
                self.env.ref('mail.test_mail_outgoing').mail_message_id.id
            ),
        ])
        self.assertTrue(notification.is_email)
        self.assertEqual(notification.email_status, 'ready')
        notification = self.env['mail.notification'].search([
            (
                'mail_message_id', '=',
                self.env.ref('mail.test_mail_exception').mail_message_id.id
            ),
        ])
        self.assertTrue(notification.is_email)
        self.assertEqual(notification.email_status, 'exception')
