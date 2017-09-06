# coding: utf-8
# Copyright 2017 Tecnativa - Pedro M. Baeza

from openerp.tests.common import TransactionCase


class TestProject(TransactionCase):

    def test_project(self):
        self.assertFalse(self.env.ref('project.project_task_data_8', False))
        self.assertFalse(self.env.ref('project.project_task_data_9').active)
