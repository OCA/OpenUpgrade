env = locals().get("env")
# create a mail with a scheduled date as char to be sure it was correctly
# migrated as datetime field in v16.
env["mail.mail"].create(
    {"body_html": "TEST date", "scheduled_date": "2023-04-12 10:05:01"}
)
env["mail.mail"].create({"body_html": "TEST empty date", "scheduled_date": ""})
env.cr.commit()
