[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat//14.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-openupgrade-)
[![Build Status](https://travis-ci.com/OCA/openupgrade.svg?branch=14.0)](https://travis-ci.com/OCA/openupgrade)
[![codecov](https://codecov.io/gh/OCA/openupgrade/branch/14.0/graph/badge.svg)](https://codecov.io/gh/OCA/openupgrade)
[![Translation Status](https://translation.odoo-community.org/widgets/openupgrade-14-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/openupgrade-14-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

![OpenUpgrade logo](/doc/source/images/OpenUpgrade.png?raw=true)
# Tools to upgrade Odoo instances from a major version to another

This <a href="https://odoo-community.org">OCA</a> project aims to provide an
Open Source upgrade path for <a href="https://github.com/odoo/odoo">Odoo</a> from one
major Odoo version to the next one.

It is hosted at <a href="https://github.com/oca/openupgrade">GitHub</a>.

For documentation, see <a href="https://doc.therp.nl/openupgrade">here</a> including:

- [introduction](doc/source/intro.rst)
- [migration process](doc/source/migration_details.rst)
- [module coverage](doc/source/status.rst)
- [development](doc/source/development.rst)
- and much more ...

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[openupgrade_framework](openupgrade_framework/) | 14.0.1.0.0 | Module to integrate in the server_wide_modules option to make upgrades between two major revisions.
[openupgrade_scripts](openupgrade_scripts/) | 14.0.1.0.0 | Module that contains all the migrations analysis and scripts for migrate Odoo SA modules.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OCA
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
