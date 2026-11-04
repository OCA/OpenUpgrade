"""Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    # odoo/enterprise
    # OCA/...
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    # odoo/enterprise
    # OCA/...
    # OCA/stock-logistics-warehouse
    "stock_move_quantity_product_uom": "stock",
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
