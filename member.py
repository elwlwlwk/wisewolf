import md5
import main
from flask import flash

def signin_validation(username, password):
	valid_pass= main.g.db.execute(\
'select pass from members where email=? or name=?', [username, username]).fetchone()
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
	overlaped_name= main.g.db.execute('select name from members where name=?',[username]).fetchone()
	if overlaped_name != None:
		flash('Already existing name! Try another name!')
		return False
	overlaped_email= main.g.db.execute('select email from members where email=?',[email]).fetchone()
	if overlaped_email != None:
		flash('Already existing email! Try another email!')
		return False
	main.g.db.execute('insert into members (name, pass, email) values (?,?,?)',\
[username, hash_pass(password), email])
	main.g.db.commit()
	return True
	
def hash_pass(password):
	return md5.md5(md5.md5(password+"wisewolf").hexdigest()\
+md5.md5("holo"+password).hexdigest()).hexdigest()


