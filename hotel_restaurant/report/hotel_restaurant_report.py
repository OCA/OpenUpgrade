import time
from report import report_sxw
import datetime
import pooler

class hotel_restaurant_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hotel_restaurant_report, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'get_res_data':self.get_res_data,
        })
        self.context=context
       
    def get_res_data(self,date_start,date_end):
        tids = self.pool.get('hotel.restaurant.reservation').search(self.cr,self.uid,[('start_date', '>=', date_start),('end_date', '<=', date_end)])
        res = self.pool.get('hotel.restaurant.reservation').browse(self.cr,self.uid,tids)
        print res
        return res

report_sxw.report_sxw('report.hotel.kot', 'hotel.restaurant.order', 'addons/hotel_restaurant/report/kot.rml',parser=hotel_restaurant_report)        
report_sxw.report_sxw('report.hotel.bill', 'hotel.restaurant.order', 'addons/hotel_restaurant/report/bill.rml',parser=hotel_restaurant_report)
report_sxw.report_sxw('report.hotel.table.res', 'hotel.restaurant.reservation', 'addons/hotel_restaurant/report/res_table.rml',parser=hotel_restaurant_report)
     