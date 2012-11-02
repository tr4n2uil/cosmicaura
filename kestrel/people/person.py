from django.contrib.auth.models import User
from kestrel.people.models import Person
from kestrel.core import utils

def edit( request, username, first_name, last_name, desc = '', phone = '', address = '', gender = 'N', dateofbirth = None, 
	edit = None,  _ts = None, csrfmiddlewaretoken = None, id = None, **kwargs ):
	kwargs[ 'page' ] = 'people/home/view'
	data = { 'valid' : False, 'errors' : None }

	try :
		u = User.objects.get( username = username )
		p = u.get_profile()
		u.first_name = first_name
		u.last_name = last_name
		p.title = first_name + ' ' + last_name
		p.desc = desc
		p.phone = phone
		p.address = address
		p.gender = gender
		if dateofbirth:
			p.dateofbirth = dateofbirth
		if p.authorize( request, action = 'edit' ):
			u.save()
			p.save()
			data[ 'valid' ] = True
		else: 
			return utils.fail( kwargs, data = data, errors = 'Not Authorized' )
		
		data[ 'user' ] = u
		data[ 'person' ] = p
		data[ 'admin' ] = 1
		data[ 'ratings' ] = set( [ p.id ] )
	except User.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Username' )
		data[ 'edit' ] = not data[ 'valid' ]	data[ 'view' ] = data[ 'valid' ]
	return utils.success( kwargs, data = data )

def passwd( request, username, current, password, cnfpasswd, passwd = None,  _ts = None, csrfmiddlewaretoken = None, **kwargs ):
	kwargs[ 'page' ] = 'people/home/view'
	data = { 'valid' : False, 'errors' : None, 'passwd' : True }
	
	try :
		u = User.objects.get( username = username )
		p = u.get_profile()
		if request.user.check_password( current ):
			if password == cnfpasswd:
				u.set_password( password )
				if p.authorize( request, action = 'edit' ):
					u.save()
				else: 
					return utils.fail( kwargs, data = data, errors = 'Not Authorized' )
			else:
				return utils.fail( kwargs, data = data, errors = 'Passwords do not match' )
		else:
			return utils.fail( kwargs, data = data, errors = 'Invalid Credentials' )
		
		data[ 'user' ] = u
		data[ 'person' ] = p
		data[ 'admin' ] = 1
		data[ 'ratings' ] = set( [ p.id ] )
	except User.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Username' )
		
	return utils.success( kwargs, data = data )

def photo( request, username, photo = None,  _ts = None, csrfmiddlewaretoken = None, id = None, **kwargs ):
	kwargs[ 'page' ] = 'people/home/view'
	data = { 'valid' : False, 'errors' : None, 'photo' : True }
	
	try :
		u = User.objects.get( username = username )
		p = u.get_profile()
		
		if p.authorize( request, action = 'edit' ):
			p.photo.file = request.FILES[ 'file' ]
			p.photo.mime = request.FILES[ 'file' ].content_type
			p.photo.save()
		else:
			return utils.fail( kwargs, data = data, errors = 'Not Authorized' )

		data[ 'user' ] = u
		data[ 'person' ] = p
		data[ 'admin' ] = 1
		data[ 'valid' ] = True
		data[ 'ratings' ] = set( [ p.id ] )
	except User.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Username' )
		# data[ 'photo' ] = not data[ 'valid' ]	# data[ 'view' ] = data[ 'valid' ]
	return utils.success( kwargs, data = data )

def reset( request, username, resetpass = None, csrfmiddlewaretoken = None, **kwargs ):
	kwargs[ 'page' ] = 'account/login'
	data = { 'valid' : False, 'errors' : None, 'reset' : True }
	
	if request.user.is_authenticated():
		return kwargs
	
	try:
		u = User.objects.get( username = username )
		if not u.is_active:
			return utils.fail( kwargs, data = data, errors = 'Invalid Username' )
		if not u.get_profile().reset():
			return utils.fail( kwargs, data = data, errors = 'Error Sending Mail' )
	except User.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Username' )
	
	return utils.success( kwargs, data = data )
