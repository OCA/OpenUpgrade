import pooler

__description__ = """This plugin return the text base on the languge and gender selected in the document"""

def dynamic_text(cr,uid,ref_text_id,**args):
    doc_id = args['document_id']
    pool = pooler.get_pool(cr.dbname)
    doc_obj = pool.get('dm.offer.document').browse(cr,uid,doc_id)
    lang_id = doc_obj.lang_id.id
    gender_id = doc_obj.gender_id.id
    criteria = [('language_id','=',lang_id),('gender_id','=',gender_id),('ref_text_id','=',ref_text_id)]
    if 'previous_step_id' in args :
        criteria.append(('previous_step_id','=',args['previous_step_id']))
    dynamic_text_id = pool.get('dm.dynamic_text').search(cr,uid,criteria)
    if dynamic_text_id :
        dynamic_text = pool.get('dm.dynamic_text').read(cr,uid,dynamic_text_id[0],['content'])['content']
        return dynamic_text
    return ""

