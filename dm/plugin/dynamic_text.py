import pooler

__description__ = """This plugin return a text based on the languge selected in the document 
                    and gender from workitem's partner gender"""

def dynamic_text(cr,uid,**args):
    doc_id = args['doc_id']
    pool = pooler.get_pool(cr.dbname)
    doc_obj = pool.get('dm.offer.document').browse(cr,uid,doc_id)
    lang_id = doc_obj.lang_id.id
    title_obj = pool.get('res.partner.title')
    if args['type'] == 'preview':
        address_id = pool.get('res.partner.address').browse(cr,uid,args['addr_id'])
    else:
        wi_id = pool.get('dm.workitem').browse(cr,uid,args['wi_id'])
        address_id = wi_id.address_id
    title_srch_id = title_obj.search(cr,uid,[('shortcut','=',address_id.title)])[0]
    gender_id = title_obj.browse(cr,uid,title_srch_id).gender_id.id
    criteria = [('language_id','=',lang_id),('gender_id','=',gender_id),('ref_text_id','=',args['ref_text_id'])]
    if 'previous_step_id' in args :
        criteria.append(('previous_step_id','=',args['previous_step_id']))
    dynamic_text_id = pool.get('dm.dynamic_text').search(cr,uid,criteria)
    print "DDDDD id ", dynamic_text_id
    if dynamic_text_id :
        dynamic_text = pool.get('dm.dynamic_text').read(cr,uid,dynamic_text_id[0],['content'])['content']
        return dynamic_text
    return ""

