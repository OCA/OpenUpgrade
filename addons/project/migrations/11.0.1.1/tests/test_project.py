# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestProject(common.TransactionCase):
    def test_convert_issues(self):
        project = self.env['project.project'].search([
            ('name', '=', 'Website for Sales & WMS (Issues)'),
        ])
        self.assertTrue(project)
        task = self.env['project.task'].search([
            ('name', '=', 'Bug in Accounts module')
        ])
        self.assertTrue(task)
        self.assertEqual(task.project_id, project)
        self.assertIn(
            self.env.ref('project.project_issue_tags_00'), task.tag_ids,
        )
