from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestHrRecruitmentMigration(TransactionCase):
    def test_properties(self):
        """
        Test that candidate properties have been moved to jobs
        """
        applicant_job_with_company = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "ou18-applicant-job-with-company"),
            ]
        )
        applicant_job_without_company = self.env["hr.applicant"].search(
            [
                ("partner_name", "=", "ou18-applicant-job-without-company"),
            ]
        )

        self.assertItemsEqual(
            applicant_job_with_company.job_id.applicant_properties_definition,
            [
                {"name": "ou18field", "type": "char", "string": "Ou18field"},
                {
                    "name": "ou18field_unused",
                    "type": "char",
                    "string": "Unused Ou18field",
                },
                {
                    "name": "ou18field_from_job",
                    "string": "Ou18field from job",
                    "type": "char",
                },
            ],
        )
        self.assertEqual(
            dict(applicant_job_with_company.applicant_properties),
            {
                "ou18field": "from ou18 for ou18-applicant-job-with-company",
                "ou18field_from_job": "from ou18 job",
                "ou18field_unused": False,
            },
        )
        self.assertItemsEqual(
            applicant_job_without_company.job_id.applicant_properties_definition,
            [
                {"name": "ou18field", "type": "char", "string": "Ou18field"},
                {
                    "name": "ou18field_unused",
                    "type": "char",
                    "string": "Unused Ou18field",
                },
            ],
        )
        self.assertEqual(
            dict(applicant_job_without_company.applicant_properties),
            {
                "ou18field": "from ou18 for ou18-applicant-job-without-company",
                "ou18field_unused": False,
            },
        )
