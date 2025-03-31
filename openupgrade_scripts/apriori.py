""" Encode any known changes to the database here
to help the matching process
"""
import os
import os.path

from odoo.modules.migration import load_script

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    "account_accountant": "accountant",
    # odoo
    # odoo/enterprise
    # OCA/...
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    # odoo/enterprise
    # OCA/sale-workflow
    "sale_order_qty_change_no_recompute": "sale",
    # OCA/...
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    # OCA/...
}

# only used here for upgrade_analysis
merged_models = {
    # odoo
    # OCA/...
}

# add knowledge from migration scripts
scripts_directory = os.path.join(os.path.dirname(__file__), "scripts")
for module_name in os.listdir(scripts_directory):
    module_dir = os.path.join(scripts_directory, module_name)
    if not os.path.isdir(module_dir):
        continue
    for version in os.listdir(module_dir):
        version_dir = os.path.join(module_dir, version)
        if not version[0].isdigit() or not os.path.isdir(version_dir):
            continue
        for script in os.listdir(version_dir):
            if not script.startswith("pre") or not script.endswith(".py"):
                continue
            migration_script = None
            try:
                migration_script = load_script(
                    os.path.join(version_dir, script),
                    ".".join([module_name, version, script]),
                )
            except Exception:
                pass
            for key, value in getattr(migration_script, "model_renames", {}):
                renamed_models.setdefault(key, value)
