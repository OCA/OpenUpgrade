import time
from report import report_sxw
import datetime
import pooler
class activity_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(activity_report, self).__init__(cr, uid, name, context)
        
        self.localcontext.update( {
            'time': time,
            'get_activity_detail': self.get_activity_detail,
            'get_room_no': self.get_room_no,
            
        })
        self.context=context
        
    def get_activity_detail(self,date_start,date_end,room_no):
        
        self.cr.execute("select hh.current_date,ppt.name as Activity,pt.name as Room,rs.login,hha.clean_start_time,hha.clean_end_time,(hha.clean_end_time-hha.clean_start_time) as duration  from hotel_housekeeping as hh " \
                        "inner join hotel_housekeeping_activities as hha on hha.a_list=hh.id " \
                        "inner join h_activity as ha on ha.id=hha.activity_name " \
                        "inner join hotel_room as hor on hor.product_id=hh.room_no " \
                        "inner join product_product as pp on pp.product_tmpl_id=hh.room_no " \
                        "inner join product_template as pt on pt.id=pp.product_tmpl_id " \
                        "inner join product_product as ppr on ppr.product_tmpl_id=ha.h_id " \
                        "inner join product_template as ppt on ppt.id=ppr.product_tmpl_id " \
                        "inner join res_users as rs on rs.id=hha.housekeeper " \
                        "where hh.current_date >= %s and hh.current_date <= %s  and hor.id= %d " \
                        ,(date_start,date_end,room_no)
                        )
                     
        res=self.cr.dictfetchall()
        print res     
        return res
   
    def get_room_no(self,room_no):
        return self.pool.get('hotel.room').browse(self.cr, self.uid, room_no).name
    
report_sxw.report_sxw('report.activity.detail', 'hotel.housekeeping', 'addons/hotel_housekeeping/report/activity_detail.rml',parser= activity_report)    