import pickle, md5

def uniq_id(data, prefix='', suffix=''):
	d = pickle.dumps(data)
	n = md5.new()
	n.update(d)
	return prefix + (n.hexdigest()[:20]) + suffix
