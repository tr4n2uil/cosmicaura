import os, shutil
from django.conf import settings
from django.db import models
from django.core.files.storage import FileSystemStorage
from kestrel.interlink.models import Node, Bridge

class OverwriteStorage( FileSystemStorage ):
    def get_available_name( self, name ):
        if os.path.exists( self.path( name ) ):
            os.remove( self.path( name ) )
        return name

# 	kestrel storage directory
class Directory( Node ):
	class Meta:
		proxy = True
	
	def add( self, *args, **kwargs ):
		if not self.type: self.type = Node.objects.get( id = settings.STORAGE_DIRECTORY_TYPE )
		return super( Directory, self ).add( *args, **kwargs )
		
		try:
			os.mkdir( self.get_path() )
		except:
			super( Directory, self ).remove( *args, **kwargs )
			raise Exception( "Unable to create Directory" + self.get_path() )
	
	def remove(self, *args, **kwargs):
		try:
			if os.path.exists( self.get_path() ):
				shutil.rmtree( self.get_path() )
			return super( Directory, self ).remove( *args, **kwargs )
		except:
			raise Exception( "Unable to Delete Directory" + self.get_path() )
	
	def rename( self, name, *args, **kwargs ):
		try:
			old_path = self.get_path()
			self.name = name
			self.set_canonical_name()
			os.rename( old_path, self.get_path() )
			self.save()
		except:
			raise Exception( "Unable to Rename Directory" + self.get_path() )
	
	def get_root( self, *args, **kwargs ):
		d = self.neighbor.filter( type = settings.STORAGE_DIRECTORY_TYPE )[ 0 ]
		return d.title
		#return settings.STORAGE_NAMES[ self.type.id - settings.STORAGE_DIRECTORY_TYPE ]
	
	def set_path( self, *args, **kwargs ):
		self.path = ''.join( [ self.parent.path, '/', self.name ] )
		return self
	
	def get_path( self, absolute = True, *args, **kwargs ):
		return self.path
		# d = self
		# path = [ '/', d.name ]
		# while( d.id != settings.STORAGE_BUCKET_ID ):
			# d = d.parent
			# path = [ '/', d.name ] + path
			# print path
		# return ''.join( ( [ settings.STORAGE_ROOT ] + path ) if absolute else path ).replace( '/', os.sep )
		# return ''.join( ( [ settings.STORAGE_ROOT[ d.type.id - settings.STORAGE_DIRECTORY_TYPE ] ] + path ) if absolute else path ).replace( '/',os.sep )

# 	upload_to callable
def get_upload_path( instance, filename ):
	if not instance.name: instance.name = filename
	return instance.get_path()

# 	kestrel storage file
class File( Node ):
	file = models.FileField( upload_to = get_upload_path, max_length = 512, storage = OverwriteStorage() )
	mime = models.CharField( max_length = 512, default = 'application/force-download' )
	read = models.CharField( max_length = 8, default = 'info' )
	rite = models.CharField( max_length = 8, default = 'add' )
	
	def add( self, period = True, *args, **kwargs ):
		if not self.type: self.type = Node.objects.get( id = settings.STORAGE_FILE_TYPE )
		return super( File, self ).add( period = period, *args, **kwargs )
	
	def write( self, request, key = 'file', *args, **kwargs ):
		self.file = request.FILES[ 'file' ]
		self.mime = request.FILES[ 'file' ].content_type
		self.desc = request.FILES[ 'file' ].name
		self.save()
	
	def rename( self, name, *args, **kwargs ):
		try:
			old_path = self.get_path()
			self.name = name
			self.set_canonical_name( period = True )
			os.rename( old_path, self.get_path() )
			self.save()
		except:
			raise Exception( "Unable to Rename File" + self.get_path() )
	
	def remove( self, *args, **kwargs ):
		try:
			if os.path.exists( self.get_path() ):
				os.remove( self.get_path() )
			return super( File, self ).remove( *args, **kwargs )
		except:
			raise Exception( "Unable to Remove File" + self.get_path() )
	
	def set_path( self, *args, **kwargs ):
		self.path = ''.join( [ self.parent.path, '/', self.name ] )
		return self
	
	def get_path( self, absolute = True, *args, **kwargs ):
		return self.path
		# d = Directory.objects.get( id = self.parent.id )
		# return ''.join( [ d.get_path( absolute ), os.sep, self.name ] )
	
	def get_public_url( self, *args, **kwargs ):
		return settings.STORAGE_URL
		#return self.neighbor.filter( type = settings.STORAGE_DIRECTORY_TYPE )[ 0 ].desc
		#return settings.STORAGE_URLS[ self.type.id - settings.STORAGE_FILE_TYPE ]
