# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestMassMailing(TransactionCase):

    def test_mass_mailing_source_id(self):
        mm = self.env.ref('mass_mailing.mass_mail_1')
        self.assertTrue(mm.source_id)
        self.assertEqual(mm.source_id.name, u"First Newsletter")
