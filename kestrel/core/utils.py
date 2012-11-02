import exceptions

# guard exception
class GuardException(exceptions.Exception):
	def __init__(self):
		return
	
	def __str__(self):
		print  "", "Unable to Authorize"

# is numeric
def is_numeric(*args):
	for value in args:
		try:
			value = float(value)
		except ValueError:
			return False
	return True

# fail
def fail(kwargs, data = { }, errors = 'Failure'):
	data['valid'] = False
	data['errors'] = errors
	kwargs['data'] = data
	return kwargs

# success
def success(kwargs, data = { }):
	data['valid'] = True
	data['errors'] = None
	kwargs['data'] = data
	return kwargs

# merge
def merge(a, b):
	for e in b:
		try: 
			a.index(e)
		except:
			a.append(e)
	return a
