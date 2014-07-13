from flask.views import View
from flask import render_template, redirect, url_for, request, session

from wisewolf.web.member import signin_validation

class RenderTemplateView(View):
	def __init__(self, template_name):
		self.template_name= template_name
	def dispatch_request(self):
		return render_template(self.template_name)

class RenderIndex(View):
	def dispatch_request(self):
		return redirect(url_for('root'))

class RenderSignin(RenderTemplateView):
	methods= ['GET', 'POST']
	def dispatch_request(self):

		if 'signed_in' in session:
			if session['signed_in']:
				return redirect(url_for('index'))
		if request.method== 'POST':
			if signin_validation(request.form['username'], request.form['password'])== True:
				session['signed_in']=True
				session['user']= request.form['username']
				return redirect(url_for('index'))
		return render_template('signin.html')

class RenderSignout(View):
	def dispatch_request(self):
		session.pop('signed_in', None)
		session.pop('user', None)
		return redirect(url_for('index'))
	
class RenderSignup(RenderTemplateView):
	methods= ['GET', 'POST']
	def dispatch_request(self):
		from member import new_member
		if request.method== 'POST':
			if new_member(request.form['username'], request.form['password'],\
request.form['email'])== True:
				return redirect(url_for('signin'))
			else:
				return redirect(url_for('signup'))
		return render_template('signup.html')	
