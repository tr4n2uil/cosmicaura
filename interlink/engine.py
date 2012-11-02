from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from kestrel.core import utils
from kestrel.interlink.models import Node
from kestrel.people.models import Person

#	1. promotes or unpromotes rating for a node
def rate( request, id, username, _ts = None, csrfmiddlewaretoken = None, **kwargs ):
	kwargs[ 'page' ] = 'kestrel/engine/rate'
	data = { 'view' : True }
	
	if not utils.is_numeric( id ): 
		return utils.fail( kwargs, data = data, errors = 'Invalid Request' )
	
	try :	
		if not request.user.is_authenticated():
			return utils.fail( kwargs, data = data, errors = 'Invalid User' )
		
		p = request.user.get_profile()
		sql = ''.join( [ 'SELECT *, exists( SELECT `interlink_bridge`.`id` from `interlink_bridge` where `src_id`=', str( p.id ),' and `sink_id`=`interlink_node`.`id` and `base`=', str( settings.LIBRARY_RATING_TYPE ),' ) as `done` from `interlink_node` WHERE `interlink_node`.`id`=', str( id ),' LIMIT 1' ] )
		
		n = Node.objects.raw( sql )[ 0 ]
		rating = -1 if n.done else 1
		
		if n.authorize( request, action = 'rate' ):
			n.rating = models.F( 'rating' ) + rating
			n.save()
			if n.done:
				n.unlink( parent = p, base = settings.LIBRARY_RATING_TYPE )
			else:
				n.link( parent = p, base = settings.LIBRARY_RATING_TYPE )
			
			n = Node.objects.raw( sql )[ 0 ]
			data[ 'node' ] = n
			if n.done:
				data[ 'ratings' ] = set( [ n.id ] )
		else:
			return utils.fail( kwargs, data = data, errors = 'Not Authorized' )
		
	except Node.DoesNotExist:
		return utils.fail( kwargs, data = data, errors = 'Invalid Node' )
		
	return utils.success( kwargs, data = data )
