from odoo.addons import mrp


def _pre_init_mrp(cr):
    """ Allow installing MRP in databases with large stock.move table (>1M records)
        - Creating the computed+stored field stock_move.is_done is terribly slow with the ORM and
          leads to "Out of Memory" crashes
    """
    # <OpenUpgrade:REMOVE>
    # don't try to add 'is_done' column, because it will fail
    # when executing the generation of records, in the openupgrade_records
    # module.
    # cr.execute("""ALTER TABLE "stock_move" ADD COLUMN "is_done" bool;""")
    # cr.execute("""UPDATE stock_move
    #                  SET is_done=COALESCE(state in ('done', 'cancel'), FALSE);""")
    pass
    # </OpenUpgrade>


mrp._pre_init_mrp = _pre_init_mrp
