env = locals().get("env")
# set company_registry in v15 to be sure we migrate it correctly to v16
env.ref("base.main_company").company_registry = "424242"
env.cr.commit()
