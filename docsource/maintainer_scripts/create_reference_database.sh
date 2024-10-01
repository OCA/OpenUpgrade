# Note: In that script, we generate a 17.0 database,
# that will be used by the OpenUpgrade CI of the 18.0 branch.

# Configuration
export VERSION=17.0

# Install account module first to ensure that the chart of accounts of l10n_generic_coa
# is installed instead of the chart of accounts of the first localization module that is encountered.
odoo-bin -d $VERSION -i account --stop-after-init --without-demo=

# Mark all interesting modules as installable
echo "update ir_module_module set state = 'uninstallable' where name like 'test%' or name like 'hw_%';" | psql $VERSION
echo "update ir_module_module set state = 'to install', demo=true where state = 'uninstalled';" | psql $VERSION

# Install all modules
odoo-bin -d $VERSION -i dummy --stop-after-init --without-demo=

# Note: Installation could fail because install modules sometime requires extra python libraries
# that are not present in the requirements.txt file. For exemple, install ``l10n_eg_edi_eta``
# requires the installation of the python library ``asn1crypto``.
# In that case, you have to
# - install manually the python library in your environment
# - run again the "set state='to install'" command
# - run again the "-i dummy" command

# put the attachment in database
cat <<EOF | odoo-bin shell -d $VERSION
env['ir.config_parameter'].set_param('ir_attachment.location', 'db')
env['ir.attachment'].force_storage()
env.cr.commit()
EOF

# Install an additional language (optional, e.g. 15.0)
cat <<EOF | odoo-bin shell -d $VERSION
lang = env.ref('base.lang_fr')
lang._activate_lang(lang.code)
env['ir.module.module'].search([('state', '=', 'installed')])._update_translations(lang.code, True)
env.cr.commit()
EOF

# Export database
sudo su postgres -c "pg_dump -d $VERSION --format=c --file=/tmp/$VERSION.psql"
