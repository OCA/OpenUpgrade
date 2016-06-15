# -*- coding: utf-8 -*-
# © 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


class TestBase(common.TransactionCase):
    def test_group_portal(self):
        # check if this group has been renamed properly
        self.assertFalse(self.env.ref('portal.group_portal',
                                      raise_if_not_found=False))
