
from osv import fields,osv

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('confirm','Confirm'),
    ('done', 'Done')
 
]

class report_hotel_reservation_status(osv.osv):
    _name = "report.hotel.reservation.status"
    _description = "Reservation By State"
    _auto = False
    _columns = {
        
        'reservation_no':fields.char('Reservation No',size=64,readonly=True),
        'nbr': fields.integer('Reservation', readonly=True),
        'state': fields.selection(AVAILABLE_STATES, 'State', size=16, readonly=True),
        
    }
    
    def init(self, cr):
        cr.execute("""
            create or replace view report_hotel_reservation_status as (
                select
                    min(c.id) as id,
                    c.reservation_no,
                    c.state,
                    count(*) as nbr
                from
                    hotel_reservation c
                group by c.state,c.reservation_no
            )""")
report_hotel_reservation_status()