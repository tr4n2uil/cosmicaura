import re
from django.conf import settings
from django.db import models
from kestrel.core import utils

# 	kestrel interlink inode
class iNode( models.Model ):

	def __unicode__( node ):
		return '%s [%s] [%d]' % ( node.title, node.name, node.id )
	
	#	1. saves node
	#	2. inherits and links guards
	#	3. links owner to node
	#	4. links node to parent
	#	5. increments count of parent
	#	guards: 'info', 'edit', 'add', 'remove', 'list', 'link', 'unlnk'
	def add( node, base = settings.INTERLINK_COLOR_ALL, ginherit = [ ], period = False, count = True, **kwargs ):
		if not node.id: 
			node.set_canonical_name( period )
			if not node.g_level:
				node.g_level = ( node.parent.g_level + 1 if node.parent.g_level >= 0 else node.parent.g_level - 1 )
			node.save()
			
			node.set_path( )
			node.save()
			
			# gs = node.parent.bridge_src.filter( sink__guard__action__in = ginherit, sink__type = settings.INTERLINK_GUARD_TYPE )
			# for g in gs:
				# g.sink.link( parent = node, base = [], weight = ( g.weight + 1 if g.weight >= 0 else g.weight - 1 ) )
			
			node.owner.link( parent = node, base = settings.INTERLINK_MEMBER_TYPE )
			node.link( parent = node.parent, base = base, owner = node.owner.id )
		
			if count:
				node.parent.count = models.F( 'count' ) + 1;
				node.parent.save()
		
		return node
	
	#	1. links node to parent
	#	2. changes weight of bridge
	#	3. adds base nodes
	def link( node, parent, base = settings.INTERLINK_COLOR_ALL, owner = 0, weight = 0, **kwargs ):
		if owner:
			b = Bridge.objects.filter( src = parent, sink = node, base = base, owner = owner )
		else:
			b = Bridge.objects.filter( src = parent, sink = node, base = base )
		if not b:
			b = Bridge.objects.create( src = parent, sink = node, base = base, owner = owner, weight = weight )
		
		# if base: 
			# b.base = utils.merge( base, b.base.all() )
		
		if weight: 
			b.weight = weight
			b.save()
		
		return node
	
	# 	1. removes base nodes
	#	2. unlinks node from parent
	def unlink( node, parent, base = None, owner = 0, **kwargs ):
		kwarg = {}
		if owner: kwarg[ 'owner' ] = owner
		if base: kwarg[ 'base' ] = base
		
		b = Bridge.objects.filter( src = parent, sink = node, **kwarg )
		if b: b.delete()
				
		return node
	
	# 	1. removes all bridges
	#	2. deletes node
	#	3. decrements count of parent
	def remove( node, count = True, **kwargs ):
		try: 
			Bridge.objects.filter( src = node.parent, sink = node ).delete()
			
			if count:
				node.parent.count = models.F( 'count' ) - 1
				node.parent.save()
			
			node.delete()
		except Node.DoesNotExist: pass
	
	def subscribe( node, count, *args, **kwargs ):
		node.subscribers = models.F( 'subscribers' ) + count
		node.save()
		node = Node.objects.get( pk = node.pk )
		return node
	
	def comment_track( node, count, *args, **kwargs ):
		node.comments = models.F( 'comments' ) + count
		node.save()
		node = Node.objects.get( pk = node.pk )
		return node
	
	def attempt_track( node, count, *args, **kwargs ):
		node.attempts = models.F( 'attempts' ) + count
		node.save()
		node = Node.objects.get( pk = node.pk )
		return node
	
	# 	1. regex name into single word
	#	2. appends count++ if required
	# 	3. TODO canonical name generating algorithm
	def set_canonical_name( node, period = False, prefix = '', *args, **kwargs ):
		if not node.name: node.name = node.title
		
		if period:
			node.name = '-'.join( re.split( r'[^\w\.]+', node.name ) )
		else:
			node.name = '-'.join( re.split( r'[^\w]+', node.name ) )
		
		if node.parent.network.filter( name = node.name, type = node.type ).count():
			if prefix: node.name = '-'.join( [ prefix, node.name ] )
			
			i = 0
			names = node.name.split( '.' )
			cname = names[ 0 ]
			while True:
				count = node.parent.network.filter( name = node.name, type = node.type ).count()
				if not count: break
				else: 
					i = i + count
					names[ 0 ] = cname + '-' + str( i )
				node.name = '.'.join( names )
		
		node.name = node.name[:120]
		return node
	
	# 	1. regex name into single word
	#	2. checks availability of name
	# 	3. returns moderated name
	def check_name( node, name, type, *args, **kwargs ):
		name = '-'.join( re.split( r'[^\w]+', name ) )
		if node.network.filter( name__startswith = name, type = type ).count():
			return False
		return name
		
	#	1. construct path from parent info
	#	2. save path in node
	def set_path( node, *args, **kwargs ):
		node.path = ''.join( [ node.parent.path, '/', '%011d' % node.id ] )
		return node
	
	#	1. renames safely
	def rename( node, name, period = False, *args, **kwargs ):
		node.name = name
		node.set_canonical_name( period )
		node.set_path()
		node.save()
	
	#	1. returns all connections
	def conns( node, base, nodes, info = False, *args, **kwargs ):
		if info:
			bs = node.bridge_src.filter( base = base, sink__in = nodes )
			weights = {}
			for b in bs:
				weights[ b.sink.id ] = b.weight
			return weights
		else:
			bs = node.bridge_src.only( 'sink' ).filter( base = base, sink__in = nodes )
			return set( list( bs.values_list( 'sink', flat = True ) ) )
	
	#	1. returns all member authorizations
	def auths( node, ucolor, nodes, *args, **kwargs ):
		bs = Node.objects.only( 'id' ).filter( models.Q( owner = node ) | models.Q( bridge_src__sink = node, bridge_src__base = ucolor ), id__in = nodes )
		return set( list( bs.values_list( 'id', flat = True ) ) )
	
	# 	KCW+ guard authorize
	#	1. check ownership
	#	2. recursively check over projected delegation graph
	def authorize( node, request, user = -1, action = 'edit', owner = True, custom = False ):
		# find user
		user = request.user.get_profile().id if request and request.user.is_authenticated() else user
		
		# check ownership
		if( owner and user == node.owner.id ):
			return True
		
		print action
		b = node.network.filter( name__contains = action, type = settings.INTERLINK_GUARD_TYPE )
		if b.count():
			b = b[0]
		else:
			b = node.g_node.network.filter( name__contains = action, type = settings.INTERLINK_GUARD_TYPE )
			if b.count():
				b = b[0]
			elif user > -1: 
				return True
			else: 
				return False
		
		print b.title
		g = b.guard
		if g.auth == 'P': return True
		
		# execute custom auth
		# if( custom ): 
			# result = custom( id, user, action )
			# if result: return True
		
		if g.auth == 'G':
			level = g.grlevel
			id = g.grroot
		elif g.auth == 'R':
			level = node.g_level
			id = node.root if node.owner != node.root else node.id
		else:
			level = node.g_level
			id = node.id
		
		moveup = level > -1
		level = level + 1 if moveup else -1*level + 1
		nodes = [ id ]
		
		# recursively check over projected delegation graph
		while level and nodes:
			level -= 1
			print nodes, user
			try:
				# find owner
				b = Bridge.objects.get( src__in = nodes, sink = user, base = g.ucolor )
				# auth success
				return True
			except Bridge.DoesNotExist:
				if level:
					# replace nodes with extended network
					if moveup:
						nodes = Bridge.objects.filter( sink__in = nodes, base = g.color ).values_list( 'src' )
					else:
						nodes = Bridge.objects.filter( src__in = nodes, base = g.color ).values_list( 'sink' )
		
		# auth fail
		return False

#	1. return path from node to user
def find_path( nodes, user, color, ucolor, moveup, length ):
	print nodes	
	if not length or not nodes:
		return None
	
	try:
		b = Bridge.objects.get( src__in = nodes, sink = user, base = ucolor )
		return ( b.src, [ b ] )
	except Bridge.DoesNotExist:
		if moveup:
			nodes_new = Bridge.objects.filter( sink__in = nodes, base = color ).values_list( 'src' )
		else:
			nodes_new = Bridge.objects.filter( src__in = nodes, base = color ).values_list( 'sink' )
		
		fp = find_path( nodes_new, user, color, ucolor, moveup, length - 1 )
		if not fp: return None
		
		if moveup:
			b = Bridge.objects.get( sink__in = nodes, src = fp[ 0 ], base = color )
			return ( b.sink, [ b ] + fp[ 1 ] )
		else:
			b = Bridge.objects.get( src__in = nodes, sink = fp[ 0 ], base = color )
			return ( b.src, [ b ] + fp[ 1 ] )

# 	kestrel interlink bridge
class Bridge( models.Model ):
	id = models.AutoField( primary_key = True )
	src = models.ForeignKey( Node, related_name = 'bridge_src', on_delete = models.CASCADE )
	sink = models.ForeignKey( Node, related_name = 'bridge_sink', on_delete = models.CASCADE )
	base = models.IntegerField( default = 0 )
	owner = models.IntegerField( default = 0 )
	weight = models.IntegerField( default = 0 )
	ctime = models.DateTimeField( auto_now_add = True )
	# base = models.ManyToManyField( Node, related_name = 'bridge_base', db_table = 'interlink_base', symmetrical = False )
	
	def __unicode__( self ):
		return ''.join( [ self.src.__str__(), ' -> ', self.sink.__str__(), ' -> ', str( self.base ) ] )

# 	kestrel interlink guard
class Guard( Node ):
	auth = models.CharField( max_length = 2, default = 'N' ) # P=public G=group N=normal
	color = models.IntegerField( default = settings.INTERLINK_COLOR_ALL )
	ucolor = models.IntegerField( default = settings.INTERLINK_MEMBER_TYPE )
	grroot = models.IntegerField( default = 0 )
	grlevel = models.IntegerField( default = 0 )
	
	def add( self, *args, **kwargs ):
		if not self.type: self.type = settings.INTERLINK_GUARD_TYPE
		super( Guard, self ).add( *args, **kwargs )
	
	def __unicode__( self ):
		return super( Guard, self ).__unicode__() + ' --' + self.auth + '--> ' + self.color.__str__()
