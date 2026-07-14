from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestHrAttendanceMigration(TransactionCase):
    def test_overtime_rules(self):
        """
        Test that overtime rules are set and there's different rules for main company
        and secondary company
        """
        default_rule = self.env.ref(
            "hr_attendance.hr_attendance_overtime_employee_schedule_rule"
        )
        self.assertEqual(default_rule.employer_tolerance, 0.5)
        secondary_ruleset = self.env["hr.attendance.overtime.ruleset"].search(
            [
                ("company_id.name", "=", "HR attendance company"),
            ]
        )
        self.assertTrue(secondary_ruleset)
        secondary_schedule_rule = secondary_ruleset.rule_ids.filtered(
            lambda x: x.timing_type == "schedule"
        )
        self.assertFalse(secondary_schedule_rule.employer_tolerance)
