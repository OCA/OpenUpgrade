env = locals().get("env")

# Image of an employee
# hr/static/img/employee_al-image.jpg
image_base64 = """
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
J5gBuNucdWrpnIge6/3HW/tjP1/cTR/T+pH/2Q==
"""

# Create res.partner
partners = [
    {
        "name": "Ponnie Hart",
        "email": "ponnie.hart@home.me",
        "phone": "+32 2 420 42 42",
        "mobile": "+32 420 42 42 42",
    },
    {
        "name": "Alanis Dubois",
        "phone": "+32 2 421 42 42",
        "mobile": "+32 421 42 42 42",
        "email": "alanis.dubois@example.com",
        "image_1920": image_base64,
    },
]
partner_ids = [env["res.partner"].create(partner) for partner in partners]

# Create res.users
users = [
    {
        "login": "ponniehart",
        "partner_id": partner_ids[0].id,
    },
    {
        "login": "alanisdubois",
        "partner_id": partner_ids[1].id,
    },
]
user_ids = [env["res.users"].create(user) for user in users]

# Create hr.employee
employees = [
    {
        "name": "Ponnie Hart",
        "job_title": "Chief Technical Officer",
        "work_phone": "(376)-310-7863",
        "mobile_phone": "(538)-672-3185",
        "work_email": "ponnie.hart87@example.com",
        "image_1920": image_base64,
        "user_id": user_ids[0].id,
    },
    {
        "name": "Alanis Dubois",
        "job_title": "Experienced Developer",
        "work_phone": "+32 2 421 42 42",
        "mobile_phone": "+32 421 42 42 42",
        "work_email": "alanis.dubois@example.com",
        "image_1920": image_base64,
        "user_id": user_ids[1].id,
    },
    {
        "name": "Anahita Oliver",
        "job_title": "Experienced Developer",
        "work_phone": "(538)-497-4804",
        "mobile_phone": "(538)-672-3185",
        "work_email": "anahita.oliver32@example.com",
        "image_1920": image_base64,
    },
]

for employee in employees:
    env["hr.employee"].create(employee)


# Create nested department
main_department = env["hr.department"].create({"name": "Main department"})
sub_department = env["hr.department"].create(
    {"name": "Sub department", "parent_id": main_department.id}
)
sub_sub_department = env["hr.department"].create(
    {"name": "Sub sub department", "parent_id": sub_department.id}
)


env.cr.commit()
