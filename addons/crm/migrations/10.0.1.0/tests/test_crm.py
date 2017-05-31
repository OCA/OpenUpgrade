# coding: utf-8
from openerp.tests import common


class TestCrm(common.TransactionCase):

    def test_crm(self):
        # Check single team is assigned
        self.assertEqual(
            self.env.ref('crm.stage_lead2').team_id,
            self.env.ref('sales_team.team_sales_department')
        )
        # Check next activities field is filled
        activity = self.env.ref('crm.crm_activity_demo_make_quote')
        self.assertEqual(
            activity.recommended_activity_ids,
            self.env.ref('crm.crm_activity_demo_followup_quote')
        )
        activity = self.env.ref('crm.crm_activity_data_meeting')
        self.assertEqual(
            activity.recommended_activity_ids,
            self.env.ref('crm.crm_activity_data_call') +
            self.env.ref('crm.crm_activity_data_email')
        )
