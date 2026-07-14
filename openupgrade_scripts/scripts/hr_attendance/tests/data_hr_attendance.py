env = locals().get("env")
main_company = env.ref("base.main_company")
main_company.overtime_company_threshold = 30
new_company = env["res.company"].create({"name": "HR attendance company"})
env.cr.commit()
