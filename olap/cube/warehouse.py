##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import locale


import mdx_input
import sqlalchemy
from sqlalchemy import *
import common
import slicer
import datetime
import pooler
import copy

class warehouse(object):
    def create_table(self, connection, table_name, data):
        measures = data[0].keys()
        measures.pop(measures.index('name'))
        engine = create_engine(connection, echo=False)
        metadata = MetaData()
        tab = Table(str(table_name), metadata, 
                      Column('name', String(100)),
                      Column('parent_id', String(100)),
                      Column('id', String(100))
                      )
        for msr in measures:
            colmn = Column(msr, String(100))
            tab.append_column(colmn)
            
        metadata.create_all(engine) 
        result = engine.execute(tab.insert(), data)
        return {}
    
    def log(self,cr,uid,cube,query,data,connection,context={}):
        if not context==False:
            log_ids = pooler.get_pool(cr.dbname).get('olap.query.logs').search( cr, uid, [('query','=', query), ('user_id','=', uid)])
            if log_ids:
                count = pooler.get_pool(cr.dbname).get('olap.query.logs').browse(cr, uid, log_ids, context)[0]
                counter = count.count + 1
                table_name = ''
                if counter>=3:
                    if len(data[0]) == 2:
                        rows = data[0][0]
                        columns = data[0][1]
                        datas = data[1]
                        result = []
                        
                        parent_list = [ rw[0] for rw in rows]
                        
                        for element in range(len(rows)):
                            res = {}
                            check_element = rows[element][0][:rows[element][0].index(rows[element][1])]
                            if check_element:
                                res['parent_id'] = str(parent_list.index(check_element))
                                res['id'] = str(element)
                            else:
                                res['parent_id'] = str(None)
                                res['id'] = str(element)
                            res['name'] = str(rows[element][1])
                            for col in range(len(columns)):
                                col_elem = columns[col][0][:columns[col][0].index(columns[col][1])+1]
                                c_element = '.'.join(map(lambda x: str(x), col_elem))
                                res[c_element] = str(datas[element][col][0])
                            result.append(res)
                        table_name = cube.name+'_'+str(count.id)+'_'+str(counter)
                        self.create_table(connection,table_name, result)
                pooler.get_pool(cr.dbname).get('olap.query.logs').write(cr, uid, log_ids, {'count':counter, 'table_name': table_name})
                return True
            else:
                logentry={}
                logentry['user_id']=uid
                logentry['cube_id']=cube.id
                logentry['query']=query
                logentry['time']= str(datetime.datetime.now())
                logentry['result_size']=0
                logentry['count']=1
                logentry['schema_id'] = cube.schema_id.id
                log_id = pooler.get_pool(cr.dbname).get('olap.query.logs').create(cr,uid,logentry)
                return log_id
        return -1
    
    def run(self, currency, qry_obj):
        schema = qry_obj.schema_id
        table_name = str(qry_obj.table_name)
        connection = schema.database_id.connection_url
        engine = create_engine(connection, echo=False)
        metadata = MetaData(engine)
        metadata.create_all(engine)
        tab = Table(table_name, metadata, autoload=True, autoload_with=engine)
        total_columns = [c.name for c in tab.columns]
        columns = []
        cols = []
        for c in tab.columns:
                if not c.name.__contains__('name') and not c.name.__contains__('id') and not c.name.__contains__('parent_id'):
                    columns.append(c.name)
                    cols.append((c.name.split('.'), str(c.name.split('.')[1])))
        result = tab.select().execute()
        res = result.fetchall()
        rows = []
#        dt = [[[]] * len(columns)] * len(res)
        for r in range(len(res)):
            if res[r][1] == str(None):
                rows.append(([str(res[r][0])], str(res[r][0])))
            else:
                rows.append(([str(res[int(res[r][1])][0]),str(res[r][0])], str(res[r][0])))
        
        data = []
        for r in range(len(res)):
            data.append(res[r][3:])
            
        datas = []
        for dd in range(len(data)):
            datas.append([])
            for d in range(len(data[dd])):
                datas[dd].append([str(data[dd][d])])
        
        final_result = ([rows, cols], datas)
        return  final_result