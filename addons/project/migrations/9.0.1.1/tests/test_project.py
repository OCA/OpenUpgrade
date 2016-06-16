# coding: utf-8
from openerp.tests.common import TransactionCase


class TestProject(TransactionCase):

    def test_project(self):
        """ Test project task priority mapping """
        self.assertEqual(
            self.env['project.task'].search([
                ('name', '=', 'Integrate Modules')]),
            '1')
