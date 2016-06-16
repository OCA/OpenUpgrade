# coding: utf-8
from openerp.tests.common import TransactionCase


class TestProject(TransactionCase):

    def test_project(self):
        """ Test project task priority mapping """
        task = self.env['project.task'].search([
            ('name', '=', 'Integrate Modules')])
        self.assertEqual(task.priority, '1')
