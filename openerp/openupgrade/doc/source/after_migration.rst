After migration
===============

When migration through OpenUpgrade is completed, you may need to make another
complete update (with --update=all parameter passed to the server) with last
Odoo official version.

OpenUpgrade keep old model tables and old columns (prefixed with
`openupgrade_legacy_` word) in PostgreSQL as a conservative strategy because
they can be used in a later migration script (or to fix an incorrect migration)
or only for reference.

After the upgraded database has been running stable for a while, you can
consider remove this extra data for saving DB space.  There's a module called
_database_cleanup_, hosted on OCA server-tools project
(https://github.com/OCA/server-tools), that allows to purge this extra data in
an intuitive way.
