import re
from django import forms
from django.core import validators
from django.contrib.auth.models import User

reserved = [ 'about', 'abhishek', 'access', 'account', 'accounts', 'add', 'address', 'adm', 'admin', 'administration', 'adult', 'advertising', 'affiliate', 'affiliates', 'ajax', 'analytics', 'anand', 'android', 'anon', 'anonymous', 'api', 'app', 'apps', 'archive', 'atom', 'auth', 'authentication', 'avatar', 'backup', 'banner', 'banners', 'base', 'bin', 'billing', 'blog', 'blogs', 'board', 'bot', 'bots', 'business', 'chat', 'cache', 'cadastro', 'calendar', 'campaign', 'careers', 'cgi', 'client', 'cliente', 'code', 'comercial', 'compare', 'config', 'connect', 'contact', 'contest', 'create', 'code', 'compras', 'css', 'dashboard', 'data', 'db', 'design', 'delete', 'demo', 'design', 'designer', 'dev', 'devel', 'dir', 'directory', 'doc', 'docs', 'domain', 'download', 'downloads', 'edit', 'editor', 'email', 'ecommerce', 'forum', 'forums', 'faq', 'favorite', 'feed', 'feedback', 'flog', 'follow', 'file', 'files', 'free', 'ftp', 'gadget', 'gadgets', 'games', 'guest', 'group', 'groups', 'help', 'home', 'homepage', 'host', 'hosting', 'hostname', 'html', 'http', 'httpd', 'https', 'hpg', 'info', 'information', 'image', 'img', 'images', 'imap', 'index', 'invite', 'intranet', 'indice', 'ipad', 'iphone', 'irc', 'java', 'javascript', 'job', 'jobs', 'js', 'kanna', 'knowledge', 'knowledgebase', 'krishna', 'kumar', 'learn', 'learning', 'log', 'login', 'logs', 'logout', 'list', 'lists', 'mail', 'mail1', 'mail2', 'mail3', 'mail4', 'mail5', 'mailer', 'mailing', 'mx', 'manager', 'marketing', 'master', 'me', 'media', 'message', 'microblog', 'microblogs', 'mine', 'mp3', 'msg', 'msn', 'mysql', 'messenger', 'mob', 'mobile', 'movie', 'movies', 'music', 'musicas', 'my', 'name', 'named', 'net', 'network', 'new', 'news', 'newsletter', 'nick', 'nickname', 'notes', 'noticias', 'ns', 'ns1', 'ns2', 'ns3', 'ns4', 'old', 'online', 'operator', 'order', 'orders', 'page', 'pager', 'pages', 'panel', 'password', 'perl', 'pic', 'pics', 'photo', 'photos', 'photoalbum', 'php', 'plugin', 'plugins', 'pop', 'pop3', 'post', 'postmaster', 'postfix', 'posts', 'profile', 'prabha', 'project', 'projects', 'promo', 'pub', 'public', 'python', 'rajan', 'random', 'register', 'registration', 'root', 'ruby', 'rss', 'sale', 'sales', 'sample', 'samples', 'script', 'scripts', 'secure', 'send', 'service', 'shop', 'sql', 'signup', 'signin', 'search', 'security', 'settings', 'setting', 'setup', 'site', 'sites', 'sitemap', 'smtp', 'soporte', 'sreya', 'sreyas', 'ssh', 'stage', 'staging', 'start', 'subscribe', 'subdomain', 'suporte', 'support', 'stat', 'static', 'stats', 'status', 'store', 'stores', 'system', 'tablet', 'tablets', 'tech', 'telnet', 'test', 'test1', 'test2', 'test3', 'teste', 'tests', 'theme', 'themes', 'tmp', 'todo', 'task', 'tasks', 'tools', 'tv', 'talk', 'unni', 'update', 'upload', 'url', 'user', 'username', 'usuario', 'usage', 'vendas', 'vibhaj', 'video', 'videos', 'visitor', 'vrinda', 'win', 'ww', 'www', 'www1', 'www2', 'www3', 'www4', 'www5', 'www6', 'www7', 'wwww', 'wws', 'wwws', 'web', 'webmail', 'website', 'websites', 'webmaster', 'workshop', 'xxx', 'xpg', 'you', 'yourname', 'yourusername', 'yoursite', 'yourdomain' ]
 
class RegistrationForm(forms.Form):
	username = forms.CharField(max_length = 30, required = True)
	email = forms.EmailField(max_length = 75, required = True)
	password1 = forms.CharField(widget=forms.PasswordInput, max_length = 30, required = True)
	password2 = forms.CharField(widget=forms.PasswordInput, max_length = 30, required = True)

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			User.objects.get(username = username)
		except User.DoesNotExist:
			if not re.match( r'^[A-Za-z][\w\-]*$', username ):
				raise forms.ValidationError("Username must contain only letters, numbers, hyphen, underscore and must begin with a letter.")
			if username in reserved:
				raise forms.ValidationError("Username is not available.")
			return username
		else:
			raise forms.ValidationError("Username is not available.")
	
	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			User.objects.get(email = email)
		except User.DoesNotExist:
			return email
		else:
			raise forms.ValidationError("Email already registered.")
	
	def clean_password2(self):
		password1 = self.cleaned_data['password1']
		password2 = self.cleaned_data['password2']

		if password1 != password2:
			raise forms.ValidationError("Passwords do not match.")
			
		return password2
	
	def save(self, new_data):
		u = User.objects.create_user(new_data['username'], new_data['email'], new_data['password1'])
		u.is_active = False
		u.save()
		return u
