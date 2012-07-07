from django.conf import settings
from django.contrib.auth.models import User, Group, Permission, check_password
from nd import ldapconnect, nd
import ldap
import datetime
from django.db import models
from models import UserLDAPAttr

def nd_set_attrs(user, attribute_tuples):
	"""
	This function takes a django.contrib.auth.models.User and a tuple of
	tuples containing ldap attribute pairs from LDAP.
	
	These attributes are stored in the django database, and are deleted
	and updated every time the user logs in.
	
	This function first attempts to find all attributes stored in the database
	for the user, and delete them.
	
	It then iterates through the attributes and sets fields on the django
	User object based on corrosponding attributes in LDAP.
	
	The rest of the fields are packaged in a UserLDAPAttr object and stored
	in the django database.
	"""
	
	# fixes a bug where if a user was a member of webteam and is now not,
	# they retain their superuser status in the django db
	user.is_staff = False
	user.is_superuser = False
	
	# find and delete all ldap attrs in the django db
	try:
		attrs_for_user = UserLDAPAttr.objects.filter(user=user)
		for a in attrs_for_user:
			a.delete()
	except Exception, e:
		print e
	attributes = []
	for att in attribute_tuples:
		key, value = att
		if key == 'uid':
			# uid -> username
			user.username = value
			attributes += [(key, value)]
		elif key == 'cn':
			# cn -> first name (unfortunately we don't separate last name in ldap)
			user.first_name = value
			attributes += [(key, value)]
		elif key == 'mail':
			# mail -> email
			user.email = value
			attributes += [(key, value)]
		elif key == 'memberOf':
			# special case for members of webteam, they get superuser status
			if value.cn == 'webteam':
				user.is_staff = True
				user.is_superuser = True
			
			# save all groups to the django db
			try:
				group = Group.objects.get(name=value.cn)
			except Group.DoesNotExist:
					if user.username == value.cn:
							#No need to save PersonalGroups
							group = None
							pass
					else:
							group = Group(name=value.cn)
							group.save()
			
			# add the user to the groups he/she is in
			if group is not None:
					user.groups.add(group)
			attributes += [(key, value.get_dn())]
		else:
			attributes += [(key, value)]
	
	# save the ldap attributes to the django db for caching
	for k,v in attributes:
		attr = UserLDAPAttr(user=user, key=k, value=v)
		attr.save()

class NetsocAuthenticationBackend(object):
	"""
	Authenticate against nd.
	"""
	supports_object_permissions = True
	supports_anonymous_user = False
	supports_inactive_user = False
	
	def authenticate(self, username=None, password=None):
		"""
		Attempts to bind to ldap using the username and password.
		
		Returns:
			None if authentication failed.
			User(username="@__LDAP_SERVER_DOWN__@") if LDAP cannot be contacted
			User(username="@__LDAP_UNEXPLAINED_ERROR__@") if any other exception occurred.
		"""
		# don't attempt to bind with a blank username or password
		if not username or not password:
			return None
		
		# fill in the dn with the username
		dn = ldapconnect.uidfmt % username

		try:
			# attempt to bind to ldap
			ldapconnect.ldap_connect(dn, password, settings.AUTH_LDAP_SERVER_URI)
		except ldap.SERVER_DOWN:
			# return the ad-hoc user storing the error
			print "ldap server down"
			return User(username="@__LDAP_SERVER_DOWN__@", password='@__LDAP_SERVER_DOWN__@')
		except ldap.INVALID_CREDENTIALS:
			# binding was unsuccessful
			print "invalid creds"
			return None
		except Exception, e:
			# return the ad-hoc user storing the error
			user = User(username="@__LDAP_UNEXPLAINED_ERROR__@", password="@__LDAP_UNEXPLAINED_ERROR__@")
			user.first_name = str(e)
			print "server error"
			return user

		# get the nd.User object for this username
		obj = nd.User(username)
		
		# grab the attribute tuples
		attrs = obj.get_all_attribute_pairs()
		try:
			# attempt to find a pre-stored user for this uid in the django database
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			# if it does not exist, create it
			user = User(username=username, password='the prodigy are fucking shit eaters')
		# save the user, so that attempting to find attrs in the django database will not exception
		user.save()
		# set the attributes on the user and the db
		nd_set_attrs(user, attrs)
		# save the user again
		user.save()
		"apparently worked"
		return user
	
	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
