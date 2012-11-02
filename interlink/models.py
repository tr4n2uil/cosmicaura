import re
from django.conf import settings
from django.db import models
from kestrel.core import utils

# 	kestrel interlink node
class Node( models.Model ):
	id = models.AutoField( primary_key = True )
	name = models.CharField( max_length = 128 )
	title = models.CharField( max_length = 256 )
	desc = models.CharField( max_length = 5120, default = '' )
	path = models.CharField( max_length = 512, default = '' )
	count = models.IntegerField( default = 0 )
	ctime = models.DateTimeField( auto_now_add = True )
	mtime = models.DateTimeField( auto_now = True )
	type = models.ForeignKey( 'self', related_name = 'node_type', default = None, on_delete = models.SET_NULL, null = True )
	owner = models.ForeignKey( 'self', related_name = 'node_owner', default = settings.INTERLINK_OWNER_ID, on_delete = models.SET_NULL, null = True )
	parent = models.ForeignKey( 'self', related_name = 'node_parent', default = None, on_delete = models.SET_NULL, null = True )
	root = models.ForeignKey( 'self', related_name = 'node_root', default = None, on_delete = models.SET_NULL, null = True )
	g_node = models.ForeignKey( 'self', related_name = 'node_guard', default = settings.INTERLINK_GUARD_DEFAULT, on_delete = models.SET_NULL, null = True )
	g_level = models.IntegerField( default = 0 )
	network = models.ManyToManyField( 'self', through = 'Bridge', related_name = 'neighbor', symmetrical = False )
	
	#	knowledge engine parameters
	rating = models.IntegerField( default = 0 )
	notecount = models.IntegerField( default = 0 )
	tagcount = models.IntegerField( default = 0 )
	
	def __unicode__( self ):
		return '%s [%s] [%d]' % ( self.title, self.name, self.id )
	
	#	1. saves node
	#	2. inherits and links guards
	#	3. links owner to node
	#	4. links node to parent
	#	5. increments count of parent
	#	guards: 'info', 'edit', 'add', 'remove', 'list', 'link', 'unlnk'
	def add( self, base = settings.INTERLINK_COLOR_ALL, ginherit = [ ], period = False, count = True, **kwargs ):
		if not self.id: 
			self.set_canonical_name( period )
			if not self.g_level:
				self.g_level = ( self.parent.g_level + 1 if self.parent.g_level >= 0 else self.parent.g_level - 1 )
				self.save()
			
			self.set_path( )
			self.save()
			
			# gs = self.parent.bridge_src.filter( sink__guard__action__in = ginherit, sink__type = settings.INTERLINK_GUARD_TYPE )
			# for g in gs:
				# g.sink.link( parent = self, base = [], weight = ( g.weight + 1 if g.weight >= 0 else g.weight - 1 ) )
			
			self.owner.link( parent = self, base = settings.INTERLINK_MEMBER_TYPE )
			self.link( parent = self.parent, base = base, owner = self.owner.id )
		
			if count:
				self.parent.count = models.F( 'count' ) + 1;
				self.parent.save()
		
		return self
	
	#	1. links node to parent
	#	2. changes weight of bridge
	#	3. adds base nodes
	def link( self, parent, base = settings.INTERLINK_COLOR_ALL, owner = 0, weight = 0, **kwargs ):
		if owner:
			b = Bridge.objects.filter( src = parent, sink = self, base = base, owner = owner )
		else:
			b = Bridge.objects.filter( src = parent, sink = self, base = base )
		if not b:
			b = Bridge.objects.create( src = parent, sink = self, base = base, owner = owner, weight = weight )
		
		# if base: 
			# b.base = utils.merge( base, b.base.all() )
		
		if weight: 
			b.weight = weight
			b.save()
		
		return self
	
	# 	1. removes base nodes
	#	2. unlinks node from parent
	def unlink( self, parent, base = None, owner = 0, **kwargs ):
		kwarg = {}
		if owner: kwarg[ 'owner' ] = owner
		if base: kwarg[ 'base' ] = base
		
		b = Bridge.objects.filter( src = parent, sink = self, **kwarg )
		if b: b.delete()
				
		return self
	
	# 	1. removes all bridges
	#	2. deletes node
	#	3. decrements count of parent
	def remove( self, count = True, **kwargs ):
		try: 
			Bridge.objects.filter( src = self.parent, sink = self ).delete()
			
			if count:
				self.parent.count = models.F( 'count' ) - 1
				self.parent.save()
			
			self.delete()
		except Node.DoesNotExist: pass
	
	# 	1. regex name into single word
	#	2. appends count++ if required
	# 	3. TODO canonical name generating algorithm
	def set_canonical_name( self, period = False, prefix = '', *args, **kwargs ):
		if not self.name: self.name = self.title
		
		if period:
			self.name = '-'.join( re.split( r'[^\w\.]+', self.name ) )
		else:
			self.name = '-'.join( re.split( r'[^\w]+', self.name ) )
		
		if self.parent.network.filter( name = self.name, type = self.type ).count():
			if prefix: self.name = '-'.join( [ prefix, self.name ] )
			
			i = 0
			names = self.name.split( '.' )
			cname = names[ 0 ]
			while True:
				count = self.parent.network.filter( name = self.name, type = self.type ).count()
				if not count: break
				else: 
					i = i + count
					names[ 0 ] = cname + '-' + str( i )
				self.name = '.'.join( names )
		
		self.name = self.name[:120]
		return self
	
	# 	1. regex name into single word
	#	2. checks availability of name
	# 	3. returns moderated name
	def check_name( self, name, type, *args, **kwargs ):
		name = '-'.join( re.split( r'[^\w]+', name ) )
		if self.network.filter( name__startswith = name, type = type ).count():
			return False
		return name
		
	#	1. construct path from parent info
	#	2. save path in self
	def set_path( self, *args, **kwargs ):
		self.path = ''.join( [ self.parent.path, '/', '%011d' % self.id ] )
		return self
	
	#	1. renames safely
	def rename( self, name, period = False, *args, **kwargs ):
		self.name = name
		self.set_canonical_name( period )
		self.set_path()
		self.save()
	
	# 	KCW+ guard authorize
	#	1. check ownership
	#	2. recursively check over projected delegation graph
	def authorize( self, request, user = -1, action = 'edit', owner = True, custom = False ):
		# find user
		user = request.user.get_profile().id if request and request.user.is_authenticated() else user
		
		# check ownership
		if( owner and user == self.owner.id ):
			return True
		
		print action
		b = self.network.filter( name__contains = action, type = settings.INTERLINK_GUARD_TYPE )
		if b.count():
			b = b[0]
		else:
			b = self.g_node.network.filter( name__contains = action, type = settings.INTERLINK_GUARD_TYPE )
			if b.count():
				b = b[0]
			elif user > -1: 
				return True
			else: 
				return False
		
		print b
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
			level = self.g_level
			id = self.root if self.owner != self.root else self.id
		else:
			level = self.g_level
			id = self.id
		
		moveup = level > -1
		level = level + 1 if moveup else -1*level + 1
		nodes = [ id ]
		
		# recursively check over projected delegation graph
		while level and nodes:
			level -= 1;
			print nodes
			try:
				# find owner
				print Bridge.objects.get( src__in = nodes, sink = user, base = g.ucolor.id )
				# auth success
				return True
			except Bridge.DoesNotExist:
				if level:
					# replace nodes with extended network
					if moveup:
						nodes = Bridge.objects.filter( sink__in = nodes, base = g.color.id ).values_list( 'src' )
					else:
						nodes = Bridge.objects.filter( src__in = nodes, base = g.color.id ).values_list( 'sink' )
		
		# auth fail
		return False

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
		return self.src.__str__() + '--> ' + self.sink.__str__()

# 	kestrel interlink guard
class Guard( Node ):
	auth = models.CharField( max_length = 2, default = 'N' ) # P=public G=group N=normal
	color = models.ForeignKey( Node, related_name = 'guard_colors', on_delete = models.SET_NULL, default = settings.INTERLINK_COLOR_ALL, null = True )
	ucolor = models.ForeignKey( Node, related_name = 'guard_ucolors', on_delete = models.SET_NULL, default = settings.INTERLINK_MEMBER_TYPE, null = True )
	grroot = models.ForeignKey( Node, null = True, related_name = 'grnode' )
	grlevel = models.IntegerField( default = 0 )
	
	def add( self, *args, **kwargs ):
		if not self.type: self.type = settings.INTERLINK_GUARD_TYPE
		super( Guard, self ).add( *args, **kwargs )
	
	def __unicode__( self ):
		return super( Guard, self ).__unicode__() + ' --' + self.auth + '--> ' + self.color.__str__()
