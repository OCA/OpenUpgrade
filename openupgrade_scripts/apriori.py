import logging

import configparser as ConfigParser

import odoo

def load_custom_config():
    openupgrade_config_path = odoo.tools.config.misc.get("openupgrade").get("config_path")
    res = {}
    if openupgrade_config_path:
        logging.info("load_custom_config from %s: ", openupgrade_config_path)
        p = ConfigParser.RawConfigParser()
        try:
            p.read([openupgrade_config_path])
            for sec in p.sections():
                res.setdefault(sec, {})
                for (name, value) in p.items(sec):
                    if value=='True' or value=='true':
                        value = True
                    if value=='False' or value=='false':
                        value = False
                    res[sec][name] = value
        except IOError:
            pass
        except ConfigParser.NoSectionError:
            pass
    else:
        logging.info("load_custom_config, openupgrade_config_path not set")

    return res

custom_config = load_custom_config()

def _get(config_name, config_base):
    return config_base | custom_config.get(config_name, {})

# ######################################################################################
# Encode any known changes to the database here to help the matching process
# ######################################################################################

# Renamed modules is a mapping from old module name to new module name
_renamed_modules = {
    # odoo
    "crm_iap_lead": "crm_iap_mine",
    "crm_iap_lead_enrich": "crm_iap_enrich",
    "l10n_eu_service": "l10n_eu_oss",
    "mail_client_extension": "mail_plugin",
    "payment_ingenico": "payment_ogone",
    # OCA/...
}

renamed_modules = _get("renamed_modules", _renamed_modules)

# Merged modules contain a mapping from old module names to other,
# preexisting module names
_merged_modules = {
    # odoo
    "account_edi_extended": "account_edi",
    "l10n_be_invoice_bba": "l10n_be",
    "l10n_ch_qr_iban": "l10n_ch",
    "l10n_se_ocr": "l10n_se",
    "payment_fix_register_token": "payment",
    "procurement_jit": "sale_stock",
    "sale_timesheet_edit": "sale_timesheet",
    "website_event_track_exhibitor": "website_event_exhibitor",
    "website_form": "website",
    "website_sale_management": "website_sale",
    # OCA/...
}

merged_modules = _get("merged_modules", _merged_modules)

# only used here for upgrade_analysis
_renamed_models = {
    # odoo
    # OCA/...
}
renamed_models = _get("renamed_models", _renamed_models)

# only used here for upgrade_analysis
_merged_models = {}
merged_models = _get("merged_models", _merged_models)
