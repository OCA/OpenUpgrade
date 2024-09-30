Maintain OpenUpgrade Repository
===============================

The following documentation is for OpenUpgrade Maintainers.

Set up the branch for a new Odoo release
----------------------------------------

.. code-block:: shell

    # Configuration
    export PREV=16.0 OLD=17.0 NEW=18.0

    git clone https://github.com/OCA/OpenUpgrade --single-branch -b $OLD
    cd OpenUpgrade

    NODOTPREV=${PREV/\./}         # e.g. 16.0 -> 160
    NODOTDOLD=${OLD/\./}          # e.g. 17.0 -> 170
    NODOTNEW=${NEW/\./}           # e.g. 18.0 -> 180
    ESCAPEDPREV=${PREV/\./\\\.}   # e.g. 16.0 -> 16\.0
    ESCAPEDOLD=${OLD/\./\\\.}     # e.g. 17.0 -> 17\.0

    # Create a new empty branch
    git checkout --orphan $NEW
    git rm -rf .
    git commit --allow-empty --no-verify -m "[INIT] $NEW: Initialize branch"
    git push origin $NEW

    # Create a dedicated branch
    git checkout -b $NEW-initialize

    # Recover all the code from the old branch,
    # - Remove coverage docsource file from old version
    # - openupgrade_framework will be migrated in a future PR.
    # - Remove scripts from old version
    git format-patch --keep-subject --stdout $NEW..$OLD -- \
        ':!docsource' \
        ':!openupgrade_framework' \
        ':!openupgrade_scripts/scripts' \
        ':!openupgrade_scripts/apriori.py' \
    | git am -3 --keep

    # Replace No-Dot Syntax (140, 150, ...)
    sed -i "s/$NODOTDOLD/$NODOTNEW/g" .github/workflows/*
    sed -i "s/$NODOTPREV/$NODOTDOLD/g" .github/workflows/*

    # Replace Doted Syntax (14.0, 15.0, ...)
    sed -i "s/$ESCAPEDOLD/$NEW/g" \
        .github/workflows/* \
        .pylintrc* \
        README.md \
        openupgrade_scripts/readme/*

    # Reset version in manifest file
    sed -i "s/17\.0\(\.[[:digit:]]\)\{3\}/$NEW\.1\.0\.0/g" openupgrade_scripts/__manifest__.py

    sed -i "s/$ESCAPEDPREV/$OLD/g" \
        .github/workflows/* \
        openupgrade_scripts/readme/*

    git commit -am "[INIT] $NEW: Replace version numbers." --no-verify

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


Finally, ``git push`` the branch on your fork, and make a pull request against OCA/$NEW branch.

Manual changes
--------------

* Execute the technical migration of ``upgrade_analysis`` from https://github.com/OCA/server-tools.

* Run the module migration, see https://github.com/OCA/OpenUpgrade/wiki/Crude-script-to-create-the-full-analysis-between-two-versions-of-Odoo. Run with Odoo configuration option module_coverage_file_folder = <some folder>.

* On success, propose the migration of ``upgrade_analysis`` into server-tools, and the analysis files into ``openupgrade_scripts``.

* Add a coverage file (e.g. docsource/modules170-180.rst)

* In the ``OpenUpgrade``/``documentation`` branch, add a new line in ``build_openupgrade_docs``.

* Push a test database for the old release to Github (see https://github.com/OCA/OpenUpgrade/wiki/How-to-create-a-reference-database)

* Execute the technical migration of ``openupgrade_framework``.

* Check files in .github/workflows for any required changes.

* Once development starts on the new edition's migration scripts, change the default branch for new PRs at https://github.com/OCA/OpenUpgrade/settings/branches.
