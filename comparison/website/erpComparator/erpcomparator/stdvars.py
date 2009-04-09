
from turbogears import view
from erpcomparator import rpc

def tg_query(*args, **kw):
    """Returns url querrystring from the provided arguments...
    for example:

    >>> print tg_query('/graph', 'pie', width=100, height=100)
    >>> "/graph/pie?width=100&height=100"

    """
    result = []
    for k, v in kw.items():
        result += ['%s=%s'%(k, v)]

    url = '/'.join([ustr(a) for a in args])
    return ((url or '') and url + '?') + '&'.join(result)

def add_root_vars(root_vars):
    return root_vars.update({'rpc': rpc})

def add_vars(vars):
    from cherrypy import root

    std_vars = {
        'root': root,
        'query': tg_query
    }

    return vars.update(std_vars)

view.root_variable_providers.append(add_root_vars)
view.variable_providers.append(add_vars)

# vim: ts=4 sts=4 sw=4 si et

