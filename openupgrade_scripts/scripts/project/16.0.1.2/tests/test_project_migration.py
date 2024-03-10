from odoo.tests import TransactionCase


class TestProjectMigration(TransactionCase):
    def test_project_allow_milestones(self):
        """Test that the allow_milestones field on a project is correctly set.
        On a database with demo data, project.group_project_milestone
        option is set to true. So allow_milestones should be true on
        projects.
        """
        projects = self.env["project.project"].search([])
        for project in projects:
            self.assertTrue(project.allow_milestones)
