env = locals().get("env")

company = env.company
company.candidate_properties_definition = [
    {"name": "ou18field", "string": "Ou18field", "type": "char"},
    {"name": "ou18field_unused", "string": "Unused Ou18field", "type": "char"},
]
job_with_company = env["hr.job"].create(
    {
        "name": "ou18-job-with-company",
        "company_id": company.id,
        "applicant_properties_definition": [
            {
                "name": "ou18field_from_job",
                "string": "Ou18field from job",
                "type": "char",
            },
        ],
    }
)
job_without_company = env["hr.job"].create(
    {
        "name": "ou18-job-without-company",
        "company_id": False,
    }
)
applicant_job_with_company = env["hr.applicant"].create(
    {
        "candidate_id": env["hr.candidate"]
        .create(
            {
                "partner_name": "ou18-applicant-job-with-company",
                "candidate_properties": {
                    "ou18field": "from ou18 for ou18-applicant-job-with-company",
                },
            }
        )
        .id,
        "job_id": job_with_company.id,
        "applicant_properties": {
            "ou18field_from_job": "from ou18 job",
        },
    }
)
applicant_job_without_company = env["hr.applicant"].create(
    {
        "candidate_id": env["hr.candidate"]
        .create(
            {
                "partner_name": "ou18-applicant-job-without-company",
                "candidate_properties": {
                    "ou18field": "from ou18 for ou18-applicant-job-without-company",
                },
            }
        )
        .id,
        "job_id": job_without_company.id,
    }
)

env.cr.commit()
