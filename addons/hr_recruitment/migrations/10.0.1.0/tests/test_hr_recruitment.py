# coding: utf-8
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestHrRecruitment(TransactionCase):
    def test_stage_job_rel(self):
        stage_obj = self.env['hr.recruitment.stage']
        job1 = self.env.ref('hr.job_developer')
        job2 = self.env.ref('hr.job_ceo')
        self.assertEqual(stage_obj.search_count([('job_id', '=', job1.id)]), 5)
        self.assertEqual(stage_obj.search_count([('job_id', '=', job2.id)]), 5)
