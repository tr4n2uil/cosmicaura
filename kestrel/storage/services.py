from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import Http404
from kestrel.storage.models import Directory, File
from kestrel.core import utils

def list( request, username, id = settings.STORAGE_BUCKET_ID, **kwargs ):
	kwargs[ 'page' ] = 'page/storage'
	data = { 'list' : True }
	
	if not utils.is_numeric( id ): 
		return utils.fail( kwargs, data = data, errors = 'Invalid Request' )
	
	data[ 'regions' ] = settings.STORAGE_NAMES if float( id ) == settings.STORAGE_BUCKET_ID else False
	user = request.user.get_profile().id if request.user.is_authenticated() else -1
	
	try :
		d = Directory.objects.get( id = id )
		u = User.objects.get( username = username )
		p = u.get_profile()
		
		if d.authorize( request, action = 'list' ):
			s = d.network.filter( bridge_base = p )
			ds = s.filter( type = settings.STORAGE_DIRECTORY_TYPE )
			data[ 'directories' ] = ds
			fs = s.filter( type = settings.STORAGE_FILE_TYPE )
			data[ 'files' ] = fs
			data[ 'valid' ] = True
		else:
			return utils.fail( kwargs, data = data, errors = 'Not Authorized' )

		data[ 'user' ] = u
		data[ 'person' ] = p
		data[ 'storage' ] = d
		data[ 'admin' ] = p.authorize( request, action = 'add' )
	except Directory.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Storage' )
	
	return utils.success( kwargs, data = data )

def add(request, username, name, type = settings.STORAGE_DIRECTORY_TYPE, id = settings.STORAGE_BUCKET_ID, _ts = None, csrfmiddlewaretoken = None, **kwargs):
	kwargs[ 'page' ] = 'storage/directory'
	data = { 'view' : True }
	
	if not utils.is_numeric( id, type ): 
		return utils.fail( kwargs, data = data, errors = 'Invalid Request' )
	
	data[ 'regions' ] = settings.STORAGE_NAMES if float( id ) == settings.STORAGE_BUCKET_ID else False
	user = request.user.get_profile().id if request.user.is_authenticated() else -1
	
	try :
		s = Directory.objects.get( id = id )
		p = request.user.get_profile() if request.user.is_authenticated() else None
		
		if d.authorize( request, action = 'add' ):
			d = Directory( name = name, owner = p, parent = s )
			if data[ 'regions' ]: d.type = int( type )
			d.add( base = settings.GRAPH_COLOR_ALL ] )
			d.link( parent = s, base = p )
			data[ 'directory' ] = d
		else:
			return utils.fail( kwargs, data = data, errors = 'Not Authorized' )
			
		data[ 'storage' ] = s
		data[ 'admin' ] = p.authorize( request, action = 'add' )
	except Directory.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Storage' )
	
	return utils.success( kwargs, data = data )

def rename( request, username, name, id, parent = settings.STORAGE_BUCKET_ID, _ts = None, csrfmiddlewaretoken = None, **kwargs ):
	kwargs[ 'page' ] = 'storage/directory'
	data = { 'view' : True }
	
	if not utils.is_numeric( id ): 
		return utils.fail( kwargs, data = data, errors = 'Invalid Request' )
	
	data[ 'regions' ] = settings.STORAGE_NAMES if float( parent ) == settings.STORAGE_BUCKET_ID else False
	user = request.user.get_profile().id if request.user.is_authenticated() else -1
	
	try :
		s = Directory.objects.get( id = parent )
		p = request.user.get_profile() if request.user.is_authenticated() else None
		
		d = Directory.objects.get( id = id )
		data[ 'directory' ] = d
		
		if d.authorize( request, action = 'edit' ):
			if d.name != name:
				d.rename( name )
		else: 
			return utils.fail( kwargs, data = data, errors = 'Not Authorized' )

		data[ 'storage' ] = s
		data[ 'admin' ] = p.authorize( request, action = 'add' )
	except Directory.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Storage' )
	
	return utils.success( kwargs, data = data )

def rmdir( request, id, parent = settings.STORAGE_BUCKET_ID, _ts = None, csrfmiddlewaretoken = None, **kwargs ):
	kwargs[ 'page' ] = 'storage/directory'
	data = { 'view' : True }
	
	if not utils.is_numeric( id ): 
		return utils.fail( kwargs, data = data, errors = 'Invalid Request' )
	
	data[ 'regions' ] = settings.STORAGE_NAMES if float( parent ) == settings.STORAGE_BUCKET_ID else False
	user = request.user.get_profile().id if request.user.is_authenticated() else -1
	
	try :
		s = Directory.objects.get( id = parent )
		p = request.user.get_profile() if request.user.is_authenticated() else None
		
		d = Directory.objects.get( id = id )
		data[ 'directory' ] = d
		
		if d.authorize( request, action = 'remove' ):
			d.remove()
		else: 
			return utils.fail( kwargs, data = data, errors = 'Not Authorized' )

		data[ 'storage' ] = s
		data[ 'admin' ] = p.authorize( request, action = 'add' )
	except Directory.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Storage' )
	
	return utils.success( kwargs, data = data )

def file( request, id, _ts = None, csrfmiddlewaretoken = None, **kwargs ):
	try:
		f = File.objects.get( id = id )
		if f.authorize( request, action = f.read ):
			response = HttpResponse( content_type = f.mime )
			response[ 'Content-Length' ] = f.file.size
			response[ 'Content-Disposition' ] = 'attachment; filename=%s' % f.desc
			response.write( open( f.get_path(), "rb" ).read() )
			return response
		else:
			print "Not Authorized to access : " + f.desc
			raise Http404
	except File.DoesNotExist:
		raise Http404
	except utils.GuardException: 
		raise Http404

def upload( request, username, name = None, id = None, parent = settings.STORAGE_BUCKET_ID, _ts = None, csrfmiddlewaretoken = None, **kwargs ):
	kwargs[ 'page' ] = 'storage/file'
	data = { 'view' : True }
	
	if( id and not utils.is_numeric( id ) ) or ( not name and not request.FILES ): 
		return utils.fail( kwargs, data = data, errors = 'Invalid Request' )
	
	if( float( parent ) == settings.STORAGE_BUCKET_ID ):
		return utils.fail( kwargs, data = data, errors = 'Objects are not allowed here.' )
	
	user = request.user.get_profile().id if request.user.is_authenticated() else -1
	
	try :
		s = Directory.objects.get( id = parent )
		p = request.user.get_profile() if request.user.is_authenticated() else None
		name = name if name else request.FILES[ 'file' ].name
		
		if not id:
			if s.authorize( request, action = 'add' ):
				f = File( name = name, type = settings.STORAGE_FILE_TYPE, owner = p, parent = s )
				f.add( base = settings.GRAPH_COLOR_ALL )
				f.link( parent = s, base = p )
				data[ 'file' ] = f
			else: 
				return utils.fail( kwargs, data = data, errors = 'Not Authorized' )
		else:
			f = File.objects.get( id = id )
			data[ 'file' ] = f
		
		if request.FILES:
			if f.authorize( request, action = 'edit' ):
				f.write( request )
			else: 
				return utils.fail( kwargs, data = data, errors = 'Not Authorized' )

		data[ 'storage' ] = s
		data[ 'admin' ] = p.authorize( request, action = 'add' )
	except Directory.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Storage' )
	
	return utils.success( kwargs, data = data )

def change( request, username, name = None, id = None, parent = settings.STORAGE_BUCKET_ID, _ts = None, csrfmiddlewaretoken = None, **kwargs ):
	kwargs[ 'page' ] = 'storage/file'
	data = { 'view' : True }
	
	if not utils.is_numeric( id ) or ( not name and not request.FILES ): 
		return utils.fail( kwargs, data = data, errors = 'Invalid Request' )
	
	if( float( parent ) == settings.STORAGE_BUCKET_ID ):
		return utils.fail( kwargs, data = data, errors = 'Objects are not allowed here.' )
	
	user = request.user.get_profile().id if request.user.is_authenticated() else -1
	
	try :
		s = Directory.objects.get( id = parent )
		p = request.user.get_profile() if request.user.is_authenticated() else None
		name = name if name else request.FILES[ 'file' ].name
		
		f = File.objects.get( id = id )
		data[ 'file' ] = f
		
		if f.authorize( request, action = 'edit' ):
			if f.name != name:
				f.rename( name )
			if request.FILES:
				f.file = request.FILES[ 'file' ]
				f.mime = request.FILES[ 'file' ].content_type
		else: 
			return utils.fail( kwargs, data = data, errors = 'Not Authorized' )

		data[ 'storage' ] = s
		data[ 'admin' ] = p.authorize( request, action = 'add' )
	except File.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid File' )
	except Directory.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Storage' )
	
	return utils.success( kwargs, data = data )

def remove( request, id, parent = settings.STORAGE_BUCKET_ID, _ts = None, csrfmiddlewaretoken = None, **kwargs ):
	kwargs[ 'page' ] = 'storage/file'
	data = { 'view' : True }
	
	if not utils.is_numeric( id ): 
		return utils.fail( kwargs, data = data, errors = 'Invalid Request' )
	
	if( float( parent ) == settings.STORAGE_BUCKET_ID ):
		return utils.fail( kwargs, data = data, errors = 'Objects are not allowed here.' )
	
	user = request.user.get_profile().id if request.user.is_authenticated() else -1
	
	try :
		s = Directory.objects.get( id = parent )
		p = request.user.get_profile() if request.user.is_authenticated() else None
		
		f = File.objects.get( id = id )
		data[ 'file' ] = f
		
		if f.authorize( request, action = 'remove' ):
			f.remove()
		else: 
			return utils.fail( kwargs, data = data, errors = 'Not Authorized' )

		data[ 'storage' ] = s
		data[ 'admin' ] = p.authorize( request, action = 'add' )
	except File.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid File' )
	except Directory.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Storage' )
	
	return utils.success( kwargs, data = data )
