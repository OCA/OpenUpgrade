# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2 import sql
import uuid

_unlink_by_xmlid = [
    # ir.actions.act_url
    'website_slides.action_open_channels',
    # ir.rule
    'website_slides.rule_slide_channel_public',
    'website_slides.rule_slide_slide_public',
    # slide.channel
    'website_slides.channel_partial',
    'website_slides.channel_private',
    'website_slides.channel_public',
]


def convert_image_attachments(env):
    mapping = {
        'slide.slide': "image",
    }
    for model, field in mapping.items():
        Model = env[model]
        attachments = env['ir.attachment'].search([
            ('res_model', '=', model),
            ('res_field', '=', field),
            ('res_id', '!=', False),
        ])
        for attachment in attachments:
            Model.browse(attachment.res_id).image_1920 = attachment.datas


def fill_slide_sequence(env):
    # First pass for assigning the same sequence as the category had
    openupgrade.logged_query(
        env.cr, sql.SQL("""
        UPDATE slide_slide ss
        SET sequence = sc.sequence
        FROM slide_category sc
        WHERE ss.{} = sc.id
        """).format(sql.Identifier(openupgrade.get_legacy_name("category_id"))),
    )
    # Second pass for getting an unique sequence number according the ID
    openupgrade.logged_query(
        env.cr, """
        UPDATE slide_slide ss
        SET sequence = sub.rank * 5
        FROM (
            SELECT id, rank()
            OVER (
                PARTITION BY channel_id ORDER BY sequence, id
            ) FROM slide_slide
        ) sub
        WHERE ss.id = sub.id""",
    )


def convert_slide_categories(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE slide_slide ADD COLUMN old_category_id int4"
    )
    openupgrade.logged_query(
        env.cr, sql.SQL("""
        INSERT INTO slide_slide (
            create_date, create_uid, write_date, write_uid, is_category,
            name, channel_id, old_category_id, sequence, slide_type
        )
        SELECT
            sc.create_date, sc.create_uid, sc.write_date, sc.write_uid, True,
            sc.name, sc.channel_id, sc.id, min(ss.sequence) - 1 as sequence, 'document'
        FROM slide_slide ss
        JOIN slide_category sc ON sc.id = ss.{category_id}
        WHERE ss.channel_id IN (
            SELECT channel_id
            FROM slide_slide
            WHERE {category_id} IS NOT NULL
        )
        GROUP BY sc.channel_id, ss.{category_id}, sc.id, sc.name
        ORDER BY sc.channel_id, ss.{category_id}, sequence
        RETURNING id
        """).format(
            category_id=sql.Identifier(openupgrade.get_legacy_name("category_id"))
        )
    )
    # Compute statistics for the categories
    rows = env.cr.fetchall()
    if rows:
        slides = env["slide.slide"].browse([x[0] for x in rows])
        slides._compute_slides_statistics()
    openupgrade.logged_query(
        env.cr, sql.SQL("""
        UPDATE slide_slide ss
        SET category_id = ss2.id
        FROM slide_slide ss2
        WHERE ss2.old_category_id = ss.{}
        """).format(sql.Identifier(openupgrade.get_legacy_name("category_id"))),
    )


def unique_channel_tokens(env):
    """Populate a unique token for each existing channel."""
    env.cr.execute("SELECT id FROM slide_channel")
    for row in env.cr.fetchall():
        env.cr.execute(
            "UPDATE slide_channel SET access_token = %s WHERE id = %s",
            (str(uuid.uuid4()), row[0])
        )


def populate_group_members(env):
    """Now the access is explicitly set by partner, but Odoo brings a mechanism for
    auto-enrolling users from certain group, so we use it for existing definitions.
    """
    env["slide.channel"].search([("enroll_group_ids", "!=", False)])._add_groups_members()


def map_channel_options(env):
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name("visibility"), "visibility", [
            ("partial", "members"),
            ("private", "members"),
        ], table="slide_channel",
    )
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name("promote_strategy"), "promote_strategy", [
            ("custom", "most_viewed"),
            ("none", "most_viewed"),
        ], table="slide_channel",
    )


def fill_slide_likes_dislikes_views(env):
    """The new structure needs an extra slide.slide.partner record for
    registering views and possible likes/dislikes.

    We add fake records here for getting the same numbers that were cumulated
    in previous versions.
    """
    openupgrade.logged_query(
        env.cr, sql.SQL("""
        INSERT INTO slide_slide_partner
        (create_uid, create_date, write_uid, write_date,
         slide_id, channel_id, partner_id, vote, completed, quiz_attempts_count)
        SELECT ss.create_uid, ss.create_date, ss.write_uid, ss.write_date,
            ss.id, ss.channel_id, 1, 1, False, 0
        FROM slide_slide ss
        CROSS JOIN generate_series(1, ss.{likes}) AS sub
        WHERE ss.{likes} > 0
        """).format(likes=sql.Identifier(openupgrade.get_legacy_name("likes")))
    )
    openupgrade.logged_query(
        env.cr, sql.SQL("""
        INSERT INTO slide_slide_partner
        (create_uid, create_date, write_uid, write_date,
         slide_id, channel_id, partner_id, vote, completed, quiz_attempts_count)
        SELECT ss.create_uid, ss.create_date, ss.write_uid, ss.write_date,
            ss.id, ss.channel_id, 1, -1, False, 0
        FROM slide_slide ss
        CROSS JOIN generate_series(1, ss.{dislikes}) AS sub
        WHERE ss.{dislikes} > 0
        """).format(dislikes=sql.Identifier(openupgrade.get_legacy_name("dislikes")))
    )
    openupgrade.logged_query(
        env.cr, sql.SQL("""
        INSERT INTO slide_slide_partner
        (create_uid, create_date, write_uid, write_date,
         slide_id, channel_id, partner_id, vote, completed, quiz_attempts_count)
        SELECT ss.create_uid, ss.create_date, ss.write_uid, ss.write_date,
            ss.id, ss.channel_id, 1, 0, False, 0
        FROM slide_slide ss
        CROSS JOIN generate_series(1, ss.{slide_views} - COALESCE(ss.{likes}, 0) - COALESCE(ss.{dislikes}, 0)) AS sub
        WHERE ss.{slide_views} > 0
        """).format(
            likes=sql.Identifier(openupgrade.get_legacy_name("likes")),
            dislikes=sql.Identifier(openupgrade.get_legacy_name("dislikes")),
            slide_views=sql.Identifier(openupgrade.get_legacy_name("slide_views")),
        )
    )


def assign_slide_owner(env):
    openupgrade.logged_query(env.cr, "UPDATE slide_slide SET user_id = create_uid")


@openupgrade.migrate()
def migrate(env, version):
    convert_image_attachments(env)
    fill_slide_sequence(env)
    convert_slide_categories(env)
    unique_channel_tokens(env)
    populate_group_members(env)
    map_channel_options(env)
    fill_slide_likes_dislikes_views(env)
    assign_slide_owner(env)
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'website_slides', 'migrations/13.0.2.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'website_slides', [
            'slide_template_published',
            'slide_template_shared',
        ],
    )
