from odoo.tests import TransactionCase


class TestHrMigration(TransactionCase):
    def test_work_contact_creation(self):
        """Make sure work_contact_id has been created"""
        anahita_oliver = self.env["hr.employee"].search(
            [("name", "=", "Anahita Oliver")]
        )
        self.assertEqual(
            anahita_oliver.mobile_phone, anahita_oliver.work_contact_id.mobile
        )
        self.assertEqual(
            anahita_oliver.work_email, anahita_oliver.work_contact_id.email
        )
        self.assertEqual(
            anahita_oliver.image_1920, anahita_oliver.work_contact_id.image_1920
        )

    def test_work_contact_link(self):
        """Make sure work_contact_id has been linked to an existing
        partner
        """
        alanis_bubois = self.env["res.partner"].search([("name", "=", "Alanis Dubois")])
        employee = self.env["hr.employee"].search([("name", "=", "Alanis Dubois")])
        self.assertEqual(alanis_bubois.id, employee.work_contact_id.id)

    def test_work_contact_no_link(self):
        """Make sure work_contact_id has not been linked to an existing
        partner
        """
        ponnie_hart = self.env["res.partner"].search([("name", "=", "Ponnie Hart")])
        employee = self.env["hr.employee"].search([("name", "=", "Ponnie Hart")])
        self.assertNotEqual(ponnie_hart.id, employee.work_contact_id.id)

    def test_master_department_id_computation(self):
        """Test that master_department_id is correctly filled"""
        main_department = self.env["hr.department"].search(
            [("name", "=", "Main department")], limit=1
        )
        sub_department = self.env["hr.department"].search(
            [("name", "=", "Sub department")], limit=1
        )
        sub_sub_department = self.env["hr.department"].search(
            [("name", "=", "Sub sub department")], limit=1
        )
        self.assertEqual(main_department.master_department_id, main_department)
        self.assertEqual(sub_department.master_department_id, main_department)
        self.assertEqual(sub_sub_department.master_department_id, main_department)
