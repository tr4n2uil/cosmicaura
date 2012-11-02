# kestrel core workflow service
import types
from django.utils import simplejson
import kestrel.core.response

# 
# input service string Service Key [kwargs] optional
# input mapping dict Service Mappings [kwargs] optional
#
# output request dict Request [kwargs] optional
#
def run(request, mappings = {}, parse = 'post', service = None, operation = None, **kwargs):
	if parse == 'post':
		data = request.POST
	elif parse == 'get':
		data = request.GET
	elif parse == 'json':
		data = simplejson.loads(request.body)
	else:
		data = {}
	
	config = mappings.get(service, None)
	print config
	if config != None:
		service = getattr(__import__(config[0], globals(), locals(), [operation if operation else config[1]], -1), operation if operation else config[1])
		kwargs = service(request, **(dict(kwargs.items() + data.items()))) # +  ([('id', id)] if id else []))))
		#service = __import__(config[0], globals(), locals(), [operation if operation else config[1]], -1)
		#kwargs = service.run(request, **(dict(kwargs.items() + data.items())))
		print kwargs
		
		# return non dict results
		if type( kwargs ) is not types.DictType:
			return kwargs
	elif service:
		print kwargs
		kwargs['page'] = service + ('/' + operation if operation else '') #+ ('/' + id if id else '')
	
	return kestrel.core.response.run(request, **kwargs)
