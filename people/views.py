from django.contrib.auth.models import User
from kestrel.people.models import Person
from kestrel.people.forms import RegistrationForm
from kestrel.core import response, utils

def register( request, **kwargs ):
	kwargs[ 'page' ] = 'account/login'
	success = False
	
	if request.user.is_authenticated():
		return response.run( request, **kwargs )
	
	if request.POST:
		form = RegistrationForm( request.POST )
		if form.is_valid():
			u = User.objects.create_user( request.POST[ 'username' ], request.POST[ 'email' ], request.POST[ 'password1' ] )
			u.get_profile().verify()
			success = True
	else:
		form = RegistrationForm()
	
	kwargs[ 'data' ] = { 'form' : form, 'success' : success, 'register' : True }
	return response.run( request, **kwargs )

def verify( request, username = None, code = None, **kwargs ):
	kwargs[ 'page' ] = 'account/verify'
	success = False
	
	if request.user.is_authenticated():
		return response.run( request, **kwargs )
	
	if username and code:
		u = User.objects.get( username = username )
		success = u.get_profile().confirm( code )
	
	kwargs[ 'data' ] = { 'success' : success, 'verify' : True }
	return response.run( request, **kwargs )
	
def profile( request, username, **kwargs ):
	kwargs[ 'page' ] = 'people/person/profile'
	data = { 'success' : False, 'errors' : None, 'view' : True }
	print username
	
	if username:
		try:
			u = User.objects.get( username = username )
			p = u.get_profile()
			data[ 'success' ] = True
			data[ 'user' ] = u
			data[ 'person' ] = p
			data[ 'admin' ] = p.authorize( request, action = 'edit' )
		except User.DoesNotExist:
			data[ 'errors' ] = 'Invalid Username'
	else:
		data[ 'errors' ] = 'Invalid Username'
	
	return utils.success( kwargs, data = data )

def credits( request, username, **kwargs ):
	kwargs[ 'page' ] = 'people/person/credits'
	data = { 'success' : False, 'errors' : None, 'view' : True }
	
	if username:
		try:
			u = User.objects.get( username = username )
			p = u.get_profile()
			data[ 'user' ] = u
			data[ 'admin' ] = p.authorize( request, action = 'edit' )
			if data['admin']:
				data[ 'success' ] = True
				data[ 'person' ] = p
			else:
				data[ 'errors' ] = 'Not Authorized'
		except User.DoesNotExist:
			data[ 'errors' ] = 'Invalid Username'
	else:
		data[ 'errors' ] = 'Invalid Username'
	
	return utils.success( kwargs, data = data )
	