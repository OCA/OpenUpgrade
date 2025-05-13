from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Add a temp float column to store the value safely
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave ADD COLUMN request_hour_to_float float;
        ALTER TABLE hr_leave ADD COLUMN request_hour_from_float float;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave SET request_hour_to_float = request_hour_to::float
        WHERE request_hour_to IS NOT NULL;
        UPDATE hr_leave SET request_hour_from_float = request_hour_from::float
        WHERE request_hour_from IS NOT NULL;

        """,
    )

    # Delete selection values BEFORE registry tries to unlink
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_model_fields_selection
        WHERE field_id IN (
            SELECT f.id
            FROM ir_model_fields f
            JOIN ir_model m ON f.model_id = m.id
            WHERE f.name = 'request_hour_to' AND m.model = 'hr.leave'
        );
        DELETE FROM ir_model_fields_selection
        WHERE field_id IN (
            SELECT f.id
            FROM ir_model_fields f
            JOIN ir_model m ON f.model_id = m.id
            WHERE f.name = 'request_hour_from' AND m.model = 'hr.leave'
        );
        """,
    )

    # Remove the Many2many relation table if it exists
    openupgrade.logged_query(
        env.cr,
        """
        DROP TABLE IF EXISTS hr_employee_hr_leave_allocation_rel CASCADE
        """,
    )

    # Optionally drop the column from the table (not usually required for M2M)
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave_allocation
        DROP COLUMN IF EXISTS employee_ids
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_rule
        WHERE id = (
            SELECT res_id FROM ir_model_data
            WHERE module = 'hr_holidays'
            AND name = 'hr_leave_allocation_rule_multicompany'
        )
        """,
    )
