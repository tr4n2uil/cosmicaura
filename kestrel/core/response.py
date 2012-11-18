# kestrel core response service
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponse

def run(request, format = None, page = 'page/home', data = {}, **kwargs):
	#if kwargs.has_key('page') and kwargs.get('page') == None:
	#	del kwargs['page']
	if data.has_key('xplore'):
		del data['xplore']
	data[ 'settings' ] = settings

	# respond json html data
	if format == '.json':
		t = get_template(page + '.html')
		html = t.render(RequestContext(request, data))
		return HttpResponse( simplejson.dumps( { 'html' : html } ), mimetype='text/plain' )
	# respond json data
	elif format == '.jsonraw':
		return HttpResponse( simplejson.dumps( kwargs[ 'data' ] ), mimetype='text/plain' )
	# respond xplore base html
	elif format:
		data['xplore'] = format
		return render_to_response(page + '.html', data, context_instance = RequestContext(request))
	# respond base html
	else:
		return render_to_response(page + '.html', data, context_instance = RequestContext(request))
