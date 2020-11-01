# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade_tools

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.modules.registry import Registry


class OpenupgradeGenerateRecordsWizard(models.TransientModel):
    _name = "openupgrade.generate.records.wizard"
    _description = "OpenUpgrade Generate Records Wizard"
    _rec_name = "state"

    state = fields.Selection([("init", "init"), ("ready", "ready")], default="init")

    def quirk_standard_calendar_attendances(self):
        """Introduced in Odoo 13. The reinstallation causes a one2many value
        in [(0, 0, {})] format to be loaded on top of the first load, causing a
        violation of database constraint."""
        for cal in ("resource_calendar_std_35h", "resource_calendar_std_38h"):
            record = self.env.ref("resource.%s" % cal, False)
            if record:
                record.attendance_ids.unlink()

    def generate(self):
        """Main wizard step. Make sure that all modules are up-to-date,
        then reinitialize all installed modules.
        Equivalent of running the server with '-d <database> --init all'

        The goal of this is to fill the records table.

        TODO: update module list and versions, then update all modules?"""
        # Truncate the records table
        if openupgrade_tools.table_exists(
            self.env.cr, "openupgrade_attribute"
        ) and openupgrade_tools.table_exists(self.env.cr, "openupgrade_record"):
            self.env.cr.execute("TRUNCATE openupgrade_attribute, openupgrade_record;")

        # Run any quirks
        self.quirk_standard_calendar_attendances()

        # Need to get all modules in state 'installed'
        modules = self.env["ir.module.module"].search(
            [("state", "in", ["to install", "to upgrade"])]
        )
        if modules:
            self.env.cr.commit()  # pylint: disable=invalid-commit
            Registry.new(self.env.cr.dbname, update_module=True)
        # Did we succeed above?
        modules = self.env["ir.module.module"].search(
            [("state", "in", ["to install", "to upgrade"])]
        )
        if modules:
            raise UserError(
                _("Cannot seem to install or upgrade modules %s")
                % (", ".join([module.name for module in modules]))
            )
        # Now reinitialize all installed modules
        self.env["ir.module.module"].search([("state", "=", "installed")]).write(
            {"state": "to install"}
        )
        self.env.cr.commit()  # pylint: disable=invalid-commit
        Registry.new(self.env.cr.dbname, update_module=True)

        # Set domain property
        self.env.cr.execute(
            """ UPDATE openupgrade_record our
            SET domain = iaw.domain
            FROM ir_model_data imd
            JOIN ir_act_window iaw ON imd.res_id = iaw.id
            WHERE our.type = 'xmlid'
                AND imd.model = 'ir.actions.act_window'
                AND our.model = imd.model
                AND our.name = imd.module || '.' || imd.name
            """
        )
        self.env.cache.invalidate(
            [
                (self.env["openupgrade.record"]._fields["domain"], None),
            ]
        )

        # Set noupdate property from ir_model_data
        self.env.cr.execute(
            """ UPDATE openupgrade_record our
            SET noupdate = imd.noupdate
            FROM ir_model_data imd
            WHERE our.type = 'xmlid'
                AND our.model = imd.model
                AND our.name = imd.module || '.' || imd.name
            """
        )
        self.env.cache.invalidate(
            [
                (self.env["openupgrade.record"]._fields["noupdate"], None),
            ]
        )

        # Log model records
        self.env.cr.execute(
            """INSERT INTO openupgrade_record
            (module, name, model, type)
            SELECT imd2.module, imd2.module || '.' || imd.name AS name,
                im.model, 'model' AS type
            FROM (
                SELECT min(id) as id, name, res_id
                FROM ir_model_data
                WHERE name LIKE 'model_%' AND model = 'ir.model'
                GROUP BY name, res_id
                ) imd
            JOIN ir_model_data imd2 ON imd2.id = imd.id
            JOIN ir_model im ON imd.res_id = im.id
            ORDER BY imd.name, imd.id""",
        )

        return self.write({"state": "ready"})
