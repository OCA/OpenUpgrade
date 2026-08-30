#!/bin/bash
set -e
# Configuration
export PREV=17.0 OLD=18.0 NEW=19.0

git clone https://github.com/OCA/OpenUpgrade --single-branch -b $OLD
cd OpenUpgrade
git fetch origin $NEW:$NEW

NODOTPREV=${PREV/\./}         # e.g. 16.0 -> 160
NODOTDOLD=${OLD/\./}          # e.g. 17.0 -> 170
NODOTNEW=${NEW/\./}           # e.g. 18.0 -> 180
ESCAPEDPREV=${PREV/\./\\\.}   # e.g. 16.0 -> 16\.0
ESCAPEDOLD=${OLD/\./\\\.}     # e.g. 17.0 -> 17\.0

# Create a dedicated branch
git checkout $NEW -b $NEW-initialize

# Recover code from the old branch:
# - bare openupgrade_scripts
# - openupgrade-specific github actions
git format-patch --keep-subject --stdout $NEW..$OLD -- \
    openupgrade_scripts \
    ':!openupgrade_scripts/scripts' \
    ':!openupgrade_scripts/apriori.py' \
    .github \
    ':!.github/workflows/pre-commit.yml' \
    ':!.github/workflows/stale.yml' \
    ':!.github/workflows/test.yml' \
    .prettierignore \
| git am -3 --keep

# Replace No-Dot Syntax (140, 150, ...)
sed -i "s/$NODOTDOLD/$NODOTNEW/g" .github/workflows/{documentation-commit.yml,test-migration.yml}
sed -i "s/$NODOTPREV/$NODOTDOLD/g" .github/workflows/{documentation-commit.yml,test-migration.yml}

# Replace Dotted Syntax (14.0, 15.0, ...)
sed -i "s/$ESCAPEDOLD/$NEW/g" \
    .github/workflows/{documentation-commit.yml,test-migration.yml} \
    openupgrade_scripts/readme/*

# Reset version in manifest file
sed -i "s/$ESCAPEDOLD\(\.[[:digit:]]\)\{3\}/$NEW\.1\.0\.0/g" openupgrade_scripts/__manifest__.py

sed -i "s/$ESCAPEDPREV/$OLD/g" \
    .github/workflows/{documentation-commit.yml,test-migration.yml} \
    openupgrade_scripts/readme/*

git commit -am "[UPD] $NEW: Replace version numbers." --no-verify

# Initialize apriori.py file
cat << EOF > ./openupgrade_scripts/apriori.py
""" Encode any known changes to the database here
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

EOF

git add ./openupgrade_scripts/apriori.py
git commit -am "[INIT] $NEW: Initialize apriori.py file." --no-verify

pre-commit run -a || pre-commit run -a
git add .
git commit -am "[FIX] $NEW: pre-commit"
