from flask import flash
from wisewolf.web.main import g
from hashlib import md5, sha512

def signin_validation(username, password):
	g.db.execute(\
"select pass from members where email='%s' or name='%s'" % (username, username))
	valid_pass= g.db.fetchone()
	if valid_pass== None:
		return False
	valid_pass= valid_pass[0]
		
	if valid_pass== hash_pass(password):
		return True
	else:
		return False

def new_member(username, password, email):
	if username== ''or password== ''or email== '':
		flash('Enter all form!')
		return False
	g.db.execute("select name from members where name='%s'" % username)
	overlaped_name= g.db.fetchone()
	if overlaped_name != None:
		flash('Already existing name! Try another name!')
		return False
	g.db.execute("select email from members where email='%s'" % email)
	overlaped_email= g.db.fetchone()
	if overlaped_email != None:
		flash('Already existing email! Try another email!')
		return False
	g.db.execute("insert into members (name, pass, email) \
values ('%s','%s','%s');" % (username, hash_pass(password), email))
	g.db.execute("commit;")
	return True
	
def hash_pass(password):
	password= password.encode("utf-8")
	return sha512(md5(password+"wisewolf".encode("utf-8")).hexdigest().encode("utf-8")\
+md5("holo".encode("utf-8")+password).hexdigest().encode("utf-8")+"holo_the_wisewolf".encode("utf-8")).hexdigest()
