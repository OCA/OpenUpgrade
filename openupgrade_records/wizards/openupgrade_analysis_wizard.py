# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# flake8: noqa: C901

import os

from odoo import fields, models
from odoo.modules import get_module_path

from .. import compare


class OpenupgradeAnalysisWizard(models.TransientModel):
    _name = "openupgrade.analysis.wizard"
    _description = "OpenUpgrade Analysis Wizard"

    server_config = fields.Many2one(
        "openupgrade.comparison.config", "Configuration", required=True
    )
    state = fields.Selection(
        [("init", "Init"), ("ready", "Ready")], readonly=True, default="init"
    )
    log = fields.Text()
    write_files = fields.Boolean(
        help="Write analysis files to the module directories", default=True
    )

    def get_communication(self):
        """
        Retrieve both sets of database representations,
        perform the comparison and register the resulting
        change set
        """

        def write_file(module, version, content, filename="openupgrade_analysis.txt"):
            # Get absolute module path
            module_path = get_module_path(module)
            if not module_path:
                return "ERROR: could not find module path:\n"

            absolute_repo_path = os.path.split(module_path)[0]
            x, relative_repo_path = os.path.split(absolute_repo_path)
            if relative_repo_path == "addons":
                # we assume that it is an Odoo module
                # (present in /odoo/odoo/addons or in /odoo/addons)
                # we so will write in the openupgrade_scripts folder
                script_module_path = os.path.join(
                    get_module_path("openupgrade_scripts"), "scripts", module
                )
                if not os.path.exists(script_module_path):
                    try:
                        os.makedirs(script_module_path)
                    except os.error:
                        return (
                            "ERROR: could not create module migrations"
                            "  directory '%s'\n" % (script_module_path)
                        )
                full_path = os.path.join(script_module_path, version)
            else:
                # It's an extra module that doesn't belong to Odoo
                # (OCA modules, Custom modules)
                # we will generate the migration script in the
                # repository of the module.
                full_path = os.path.join(module_path, "migrations", version)

            if not os.path.exists(full_path):
                try:
                    os.makedirs(full_path)
                except os.error:
                    return "ERROR: could not create migrations directory" " '%s'\n" % (
                        full_path
                    )
            logfile = os.path.join(full_path, filename)
            try:
                f = open(logfile, "w")
            except Exception:
                return "ERROR: could not open file %s for writing:\n" % logfile
            f.write(content)
            f.close()
            return None

        self.ensure_one()
        connection = self.server_config.get_connection()
        remote_record_obj = connection.env["openupgrade.record"]
        local_record_obj = self.env["openupgrade.record"]

        # Retrieve field representations and compare
        remote_records = remote_record_obj.field_dump()
        local_records = local_record_obj.field_dump()
        res = compare.compare_sets(remote_records, local_records)

        # Retrieve xml id representations and compare
        flds = ["module", "model", "name", "noupdate", "prefix", "suffix", "domain"]
        local_xml_records = [
            {field: record[field] for field in flds}
            for record in local_record_obj.search([("type", "=", "xmlid")])
        ]
        remote_xml_record_ids = remote_record_obj.search([("type", "=", "xmlid")])
        remote_xml_records = [
            {field: record[field] for field in flds}
            for record in remote_record_obj.read(remote_xml_record_ids, flds)
        ]
        res_xml = compare.compare_xml_sets(remote_xml_records, local_xml_records)

        # Retrieve model representations and compare
        flds = ["module", "model", "name", "model_original_module", "model_type"]
        local_model_records = [
            {field: record[field] for field in flds}
            for record in local_record_obj.search([("type", "=", "model")])
        ]
        remote_model_record_ids = remote_record_obj.search([("type", "=", "model")])
        remote_model_records = [
            {field: record[field] for field in flds}
            for record in remote_record_obj.read(remote_model_record_ids, flds)
        ]
        res_model = compare.compare_model_sets(
            remote_model_records, local_model_records
        )

        affected_modules = sorted(
            {
                record["module"]
                for record in remote_records
                + local_records
                + remote_xml_records
                + local_xml_records
                + remote_model_records
                + local_model_records
            }
        )

        # reorder and output the result
        keys = ["general"] + affected_modules
        modules = {
            module["name"]: module
            for module in self.env["ir.module.module"].search(
                [("state", "=", "installed")]
            )
        }
        general = ""
        for key in keys:
            contents = "---Models in module '%s'---\n" % key
            if key in res_model:
                contents += "\n".join([str(line) for line in res_model[key]])
                if res_model[key]:
                    contents += "\n"
            contents += "---Fields in module '%s'---\n" % key
            if key in res:
                contents += "\n".join([str(line) for line in sorted(res[key])])
                if res[key]:
                    contents += "\n"
            contents += "---XML records in module '%s'---\n" % key
            if key in res_xml:
                contents += "\n".join([str(line) for line in res_xml[key]])
                if res_xml[key]:
                    contents += "\n"
            if key not in res and key not in res_xml and key not in res_model:
                contents += "---nothing has changed in this module--\n"
            if key == "general":
                general += contents
                continue
            if compare.module_map(key) not in modules:
                general += (
                    "ERROR: module not in list of installed modules:\n" + contents
                )
                continue
            if key not in modules:
                # no need to log in general the merged/renamed modules
                continue
            if self.write_files:
                error = write_file(key, modules[key].installed_version, contents)
                if error:
                    general += error
                    general += contents
            else:
                general += contents

        # Store the general log in as many places as possible ;-)
        if self.write_files and "base" in modules:
            write_file(
                "base",
                modules["base"].installed_version,
                general,
                "openupgrade_general_log.txt",
            )
        self.server_config.write({"last_log": general})
        self.write({"state": "ready", "log": general})

        return {
            "name": self._description,
            "view_mode": "form",
            "res_model": self._name,
            "type": "ir.actions.act_window",
            "res_id": self.id,
        }
