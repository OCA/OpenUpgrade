from openupgradelib import openupgrade

_xmlid_renames = [
    (
        "crm_iap_mine.crm_iap_lead_industry_30",
        "crm_iap_mine.crm_iap_mine_industry_30_155",
    ),
    ("crm_iap_mine.crm_iap_lead_industry_33", "crm_iap_mine.crm_iap_mine_industry_33"),
    ("crm_iap_mine.crm_iap_lead_industry_86", "crm_iap_mine.crm_iap_mine_industry_86"),
    (
        "crm_iap_mine.crm_iap_lead_industry_114",
        "crm_iap_mine.crm_iap_mine_industry_114",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_136",
        "crm_iap_mine.crm_iap_mine_industry_136",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_148",
        "crm_iap_mine.crm_iap_mine_industry_148",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_149",
        "crm_iap_mine.crm_iap_mine_industry_149",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_150",
        "crm_iap_mine.crm_iap_mine_industry_150_151",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_152",
        "crm_iap_mine.crm_iap_mine_industry_152",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_154",
        "crm_iap_mine.crm_iap_mine_industry_153_154",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_160",
        "crm_iap_mine.crm_iap_mine_industry_160",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_161",
        "crm_iap_mine.crm_iap_mine_industry_161",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_162",
        "crm_iap_mine.crm_iap_mine_industry_162",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_163",
        "crm_iap_mine.crm_iap_mine_industry_163",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_165",
        "crm_iap_mine.crm_iap_mine_industry_165",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_166",
        "crm_iap_mine.crm_iap_mine_industry_166",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_167",
        "crm_iap_mine.crm_iap_mine_industry_167",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_168",
        "crm_iap_mine.crm_iap_mine_industry_168",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_238",
        "crm_iap_mine.crm_iap_mine_industry_238",
    ),
    (
        "crm_iap_mine.crm_iap_lead_industry_239",
        "crm_iap_mine.crm_iap_mine_industry_239",
    ),
    ("crm_iap_mine.crm_iap_lead_role_1", "crm_iap_mine.crm_iap_mine_role_1"),
    ("crm_iap_mine.crm_iap_lead_role_2", "crm_iap_mine.crm_iap_mine_role_2"),
    ("crm_iap_mine.crm_iap_lead_role_3", "crm_iap_mine.crm_iap_mine_role_3"),
    ("crm_iap_mine.crm_iap_lead_role_4", "crm_iap_mine.crm_iap_mine_role_4"),
    ("crm_iap_mine.crm_iap_lead_role_5", "crm_iap_mine.crm_iap_mine_role_5"),
    ("crm_iap_mine.crm_iap_lead_role_6", "crm_iap_mine.crm_iap_mine_role_6"),
    ("crm_iap_mine.crm_iap_lead_role_7", "crm_iap_mine.crm_iap_mine_role_7"),
    ("crm_iap_mine.crm_iap_lead_role_8", "crm_iap_mine.crm_iap_mine_role_8"),
    ("crm_iap_mine.crm_iap_lead_role_9", "crm_iap_mine.crm_iap_mine_role_9"),
    ("crm_iap_mine.crm_iap_lead_role_10", "crm_iap_mine.crm_iap_mine_role_10"),
    ("crm_iap_mine.crm_iap_lead_role_11", "crm_iap_mine.crm_iap_mine_role_11"),
    ("crm_iap_mine.crm_iap_lead_role_12", "crm_iap_mine.crm_iap_mine_role_12"),
    ("crm_iap_mine.crm_iap_lead_role_13", "crm_iap_mine.crm_iap_mine_role_13"),
    ("crm_iap_mine.crm_iap_lead_role_14", "crm_iap_mine.crm_iap_mine_role_14"),
    ("crm_iap_mine.crm_iap_lead_role_15", "crm_iap_mine.crm_iap_mine_role_15"),
    ("crm_iap_mine.crm_iap_lead_role_16", "crm_iap_mine.crm_iap_mine_role_16"),
    ("crm_iap_mine.crm_iap_lead_role_17", "crm_iap_mine.crm_iap_mine_role_17"),
    ("crm_iap_mine.crm_iap_lead_role_18", "crm_iap_mine.crm_iap_mine_role_18"),
    ("crm_iap_mine.crm_iap_lead_role_19", "crm_iap_mine.crm_iap_mine_role_19"),
    ("crm_iap_mine.crm_iap_lead_role_20", "crm_iap_mine.crm_iap_mine_role_20"),
    ("crm_iap_mine.crm_iap_lead_role_21", "crm_iap_mine.crm_iap_mine_role_21"),
    ("crm_iap_mine.crm_iap_lead_role_22", "crm_iap_mine.crm_iap_mine_role_22"),
    ("crm_iap_mine.crm_iap_lead_seniority_1", "crm_iap_mine.crm_iap_mine_seniority_1"),
    ("crm_iap_mine.crm_iap_lead_seniority_2", "crm_iap_mine.crm_iap_mine_seniority_2"),
    ("crm_iap_mine.crm_iap_lead_seniority_3", "crm_iap_mine.crm_iap_mine_seniority_3"),
    (
        "crm_iap_mine.seq_crm_iap_lead_mining_request",
        "crm_iap_mine.ir_sequence_crm_iap_mine",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.rename_columns(
        env.cr,
        {
            "crm_iap_lead_industry": [
                ("reveal_id", "reveal_ids"),
            ],
        },
    )
