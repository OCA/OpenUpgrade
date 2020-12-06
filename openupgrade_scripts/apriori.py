""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    "partner_bank_active": "base",
}

# only used here for upgrade_analysis
renamed_models = {}

# only used here for upgrade_analysis
merged_models = {}
