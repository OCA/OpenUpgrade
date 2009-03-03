
import mdx_input
import sqlalchemy
import common
import slicer
import datetime
import pooler

import copy

class mapper(object):
    def __init__(self, size):
        self.size = size

class query(object):
    def __init__(self, axis, cube, slicer_obj=None, *args):
        print ">>>>>>>>>>>>>>In the query init >>>>>>>>>",axis,"\n Cube>>",cube,slicer_obj
        super(query, self).__init__()
        self.object = False
        self.cube = cube
        self.axis = axis
        if not slicer_obj:
            slicer_obj = slicer.slicer([])
        self.slicer = slicer_obj

    #
    # Generate the cube with 'False' values
    # This function could be improved
    #
    def _cube_create(self, cube_size):
        cube_data = [False]
        while cube_size:
            newcube = []
            for i in range(cube_size.pop()):
                newcube.append(copy.deepcopy(cube_data))
            cube_data = newcube
        return cube_data

    def run(self):
        db = sqlalchemy.create_engine(self.object.schema_id.database_id.connection_url,encoding='utf-8')
        metadata = sqlalchemy.MetaData(db)
        print 'Connected to database...', self.object.schema_id.database_id.connection_url

        #
        # Compute axis
        #

        axis = []
        axis_result = []
        cube_size = []
        cross = False
        print "\n >>> In the query run>>>",self.axis.name
        print "\n >>> In the query run>>>",self.axis


        for ax in self.axis:
            print ">>>>>>>> In the run loop >>>>>>>>>",ax.name
            if ax.name == 'cross':
                print ">>>>>>>> I made the cross >>>>>>>>>>>"
                cross = ax.run(metadata)
                '''
                    It is assumed the result will be made and the 
                    the cross comes after in the seqence 

                    crossjoin({[City].[all],[city].children},{[Users].children}) on rows / columns 
                    Following this as the syntax 
                    crossjoin ({axis},{crossjoin element})

                    We here try to combine the values of  the axis got with the crossjoin lement 
                    We make the result with the cross + adding the where clause needed and modifying the values
                '''
                
                res = [(item0,item1) for item0 in result for item1 in cross]
                print "To see the length of the result ,cross and res >>",len(result),len(cross),len(res)
                print ">>>>>This is the res i cartesian product of the axis and cross>>>>>>>>>>>",res
                print ">>>>>>>>>>>>. this is the axis so far made >>>>>>>>>",axis[0]
                count = 0 
                value = []
                for r,r1 in res:
                    print " This is the r value made >>>>>>>>>",r['value'],r1['value']
                    value.append([(item0[0],[item0[1],str(item1[1])])for item0 in r['value'] for item1 in r1['value']])
                    print " This is the r value made after >>>>>>>>>",value
#                axis[0]= r
                index = 0
                for r,r1 in res:
                    r['value'] = value[index]
                    index = index + 1
#                result = res[0]
#                x = axis.pop()
#                print "\n\n\n This is what poped >>>>>>>>>>>>>>>>>",x
#                print "\n\n\n This is what to be appended >>>>>>",result
#                print x
#                axis_result.pop()
#                axis_result.append(value)
#                axis.append(result)
#                print x
            else:
                result = ax.run(metadata)
                length = 0
                axis_result2 = []
                for r in result:
                    length += len(r['value'])
                    axis_result2 += map(lambda x: (map(lambda y: y or False,x[0]),x[1] or False), r['value'])
                print "\n\n\n %%%%%%%%%%>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",axis_result2
                axis_result.append(axis_result2)
                axis.append(result)
                cube_size.append(length)

        cube_data = self._cube_create(cube_size)
        cr = []
#        if cross:
#            cr = cross.run(metadata)
        slice = self.slicer.run(metadata)
        position = 0
        ax = []
        print "\n\n This is the axis o...... ....  ... ",axis
        for subset in common.xcombine(*axis):
#            print "\n\n in the subset >>>>>>>>>",subset
            select,table_fact = self.cube.run(metadata)
            for s in subset+slice:
                print ">>>>>>>>>>>>>s >>>>>>>>>>",s
#                s['value']
#                'value': [(['Order Date', 2008.0], 2008.0)],
                for key,val in s['query'].items():
                    for v in val:
                        if key=='column':
                            v = v.label('p_%d' % (position,))
                            position += 1
                            select.append_column(v)
                        elif key=='whereclause':
                            print '\n ~~~~~~~~Adding Slicer ',v
                            select.append_whereclause(v)
                        elif key=='group_by':
                            select.append_group_by(v)
                        else:
                            raise 'Error, %s not implemented !'% (key,)
            metadata.bind.echo = True
            print ">>>>>>>>>>>IN the QUERY<<<<<<<<<<<<<<<<<",select

            query = select.execute()
            result = query.fetchall()
            for record in result:
                cube = cube_data
                r = list(record)
                value = False
                for s in subset:
                    cube = s['axis_mapping'].cube_set(cube, r, s['delta'])
                    value = s['axis_mapping'].value_set(r) or value
                for s in slice:
                    value = s['axis_mapping'].value_set(r) or value

                if value:
                    assert not cube[0], 'Already a value in cube, this is a bug !'
                    cube[0] = value

        i=0
        for a in cube_data:
            i=i+1;
        return (axis_result, cube_data)

    def preprocess(self):
        wrapper = mdx_input.mdx_input()
        wrapper.parse(self)

    def validate(self, schema):
        """ This function takes a query object and validate and assign
        fact data to it. Browse object from Tiny ERP"""
        cube = self.cube.validate(schema)
        self.object = cube
        if not self.object:
            raise "Cube '%s' not found in the schema '%s' !"%(cube.name, schema.name)
        self.slicer.validate(cube)

        for axis in self.axis:
            print ">>>>>>>> axis validate >>>>>>>>>",axis
            axis.validate(cube)
        for dimension in cube.dimension_ids:
            pass
        return True,cube

    def __repr__(self):
        res = '<olap.query ['+str(self.cube)+']\n'
        for l in self.axis:
            res+= '\tAxis: '+str(l)+'\n'
        res+= '\tSlicer:\n'+str(self.slicer)+'\n'
        res += '>'
        return res

    def log(self,cr,uid,cube,query,context={}):
        if not context==False:
            print "Logging Query..."
            logentry={}
            logentry['user_id']=uid
            logentry['cube_id']=cube.id
            logentry['query']=query
            logentry['time']= str(datetime.datetime.now())
            logentry['result_size']=0
            log_id = pooler.get_pool(cr.dbname).get('olap.query.logs').create(cr,uid,logentry)
            return log_id
        return -1
# vim: ts=4 sts=4 sw=4 si et
