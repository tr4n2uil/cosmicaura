import datetime, random, hashlib, pytz
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.db import models
# from django.db.models.signals import post_save
from kestrel.interlink.models import Node
from kestrel.storage.models import File, Directory

# 	kestrel people person
class Person( Node ):
	user = models.OneToOneField( User )
	phone = models.CharField( max_length = 32, default = '' )
	address = models.CharField( max_length = 512, default = '' )
	dateofbirth = models.DateField( null = True )
	gender = models.CharField( max_length = 1, choices = ( ( 'M', 'Male' ), ( 'F', 'Female' ), ( 'N', 'Not Specified' ) ), default = 'N' )
	photo = models.OneToOneField( File )
	uihome = models.OneToOneField( Directory, related_name = 'person_uihome' )
	stghome = models.OneToOneField( Directory, related_name = 'person_stghome' )
	activation_key = models.CharField( max_length = 40, null = True )
	key_expires = models.DateTimeField( null = True )
	credits = models.IntegerField( default = 50 )
	
	def add( self, *args, **kwargs ):
		if not self.type: self.type = Node.objects.get( id = settings.PEOPLE_PERSON_TYPE )
		if not self.visibility: self.visibility = 1
		super( Person, self ).add( *args, **kwargs )
	
	def set_path( self, *args, **kwargs ):
		self.path = ''.join( [ self.parent.path, '/', self.name ] )
		return self
	
	#	should be called for valid person only not page
	def verify( self, *args, **kwargs ):
		salt = hashlib.sha1( str( random.random() ) ).hexdigest()[ :5 ]
		self.activation_key = hashlib.sha1( salt + self.user.username ).hexdigest()
		self.key_expires = datetime.datetime.today().replace( tzinfo = pytz.UTC ) + datetime.timedelta( settings.PEOPLE_VERIFY_EXPIRY )
		self.save()
		self.user.is_active = False
		self.user.save()
		email = EmailMessage( 
			settings.PEOPLE_VERIFY_SUBJECT, 
			settings.PEOPLE_VERIFY_BODY % { 'username' : self.user.username, 'verify' : self.activation_key }, 
			to = [ self.user.email ], 
			from_email = settings.DEFAULT_FROM_EMAIL 
		)
		return email.send()
	
	def confirm( self, code, *args, **kwargs ):
		if self.activation_key == code and self.key_expires > datetime.datetime.today().replace( tzinfo = pytz.UTC ):
			self.user.is_active = True
			self.user.save()
			return True
		return False
	
	def reset( self, *args, **kwargs ):
		salt = hashlib.sha1( str( random.random() ) ).hexdigest()[ :5 ]
		password = hashlib.sha1( salt + self.user.username ).hexdigest()[ :8 ]
		self.user.set_password( password )
		self.user.save()
		email = EmailMessage( 
			settings.PEOPLE_RESET_SUBJECT, 
			settings.PEOPLE_RESET_BODY % { 'username' : self.user.username, 'password' : password }, 
			to = [ self.user.email ],
			from_email = settings.DEFAULT_FROM_EMAIL
		)
		return email.send()
	
	# 	TODO logs
	def transaction( self, amount, payto, *args, **kwargs ):
		if self.credits < amount: return False
		if amount > 0:
			self.credits = models.F( 'credits' ) - amount
			self.save()
			self = Person.objects.get( id = self.id )
			
			payto.credits = models.F( 'credits' ) + amount
			payto.save()
		return True

# 	register handler for user
def create_person_main( sender, instance, created, **kwargs ):
    if created:
		stghome = Directory( name = instance.username, parent = Node.objects.get( id = settings.PEOPLE_PERSON_STORAGE_HOME ) )
		stghome.add()
		
		uihome = Directory( name = instance.username, parent = Node.objects.get( id = settings.PEOPLE_PERSON_UI_HOME ) )
		uihome.add()
		
		file = File( name = 'photo.png', mime = 'image/png', parent = uihome )
		file.add()
		
		person = Person( 
			user = instance, 
			name = instance.username, 
			title = instance.username,
			photo = file, 
			uihome = uihome, 
			stghome = stghome, 
			parent = Node.objects.get( id = settings.PEOPLE_ID ),
			g_node = Node.objects.get( id = settings.PEOPLE_GUARD )
		)
		person.add()
		# person.add( parent = person )
		
		uihome.owner = person
		uihome.save()
		stghome.owner = person
		stghome.save()
		file.owner = person
		file.save()
		person.owner = person
		person.save()

# post_save.connect( create_person, sender = User )
__import__( settings.PEOPLE_CONNECT_MODULE )
