[![Pre-commit Status](https://github.com/OCA/OpenUpgrade/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/OCA/OpenUpgrade/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/OCA/OpenUpgrade/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/OCA/OpenUpgrade/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/OCA/OpenUpgrade/branch/16.0/graph/badge.svg)](https://codecov.io/gh/OCA/openupgrade)


<!-- /!\ do not modify above this line -->

![OpenUpgrade logo](https://oca.github.io/OpenUpgrade/_images/OpenUpgrade.png)

# Tools to upgrade Odoo instances from a major version to another

This <a href="https://odoo-community.org">OCA</a> project aims to provide an
Open Source upgrade path for <a href="https://github.com/odoo/odoo">Odoo</a> from one
major Odoo version to the next one.

It is hosted at <a href="https://github.com/oca/openupgrade">GitHub</a>.

For documentation, see <a href="https://oca.github.io/OpenUpgrade">here</a> including:

- [introduction](https://oca.github.io/OpenUpgrade/intro.html)
- [migration process](https://oca.github.io/OpenUpgrade/migration_details.html)
- [module coverage](https://oca.github.io/OpenUpgrade/status.html)
- [development](https://oca.github.io/OpenUpgrade/development.html)
- and much more ...

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[openupgrade_framework](openupgrade_framework/) | 16.0.1.0.0 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) [![StefanRijnhart](https://github.com/StefanRijnhart.png?size=30px)](https://github.com/StefanRijnhart) [![hbrunn](https://github.com/hbrunn.png?size=30px)](https://github.com/hbrunn) | Module to integrate in the server_wide_modules option to make upgrades between two major revisions.
[openupgrade_scripts](openupgrade_scripts/) | 16.0.1.0.3 |  | Module that contains all the migrations analysis and scripts for migrate Odoo SA modules.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
