'''
* Daniel Olivas
* CS 496
* 3/18/18
* Final Project -- Cloud Only
'''

import datetime
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import json
import jinja2
import os
import random
import string
import urllib
import webapp2

#https://youtu.be/Unl0dZ6p2xw -- tutorial for jinja2
JINJA_ENV = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + "/template"))

CLIENT_ID = "1018435542096-d7vhau8d45gi4gdma8tf5gt63k57jtqe.apps.googleusercontent.com"
CLIENT_SECRET = "aa26Ym7H1xXVliG0pEP1D2f2"
REDIRECT_URL = "https://olivas-final-project.appspot.com/oauth"

#https://pythontips.com/2013/07/28/generating-a-random-string/-- create a random string of letters & numbers
STATE = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])


class User(ndb.Model):
	id = ndb.StringProperty()
	name = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	token = ndb.StringProperty()


class ToDo(ndb.Model):
	id = ndb.StringProperty()
	task = ndb.StringProperty(required=True)
	user_id = ndb.StringProperty()
	completed = ndb.BooleanProperty()
	date = ndb.StringProperty()

		
class UserHandler(webapp2.RequestHandler):
	def post(self):
		allUsers = User.query()
		user_exists = False
		for u in allUsers:
			if u.token == self.request.headers['Authorization']:
				user_exists = True
		if user_exists:
			self.response.set_status(401)
			self.response.write('Invalid Access Token')
		else:
			head_data = self.request.headers
			user_data = json.loads(self.request.body)
			new_user = User(name=user_data['name'], email=user_data['email'])
			new_user.token = head_data['Authorization']
			new_user.put()
			new_user.id = new_user.key.urlsafe()
			user_dict = new_user.to_dict()
			user_dict['self'] = '/user/' + new_user.key.urlsafe()
			new_user.put()
			self.response.write(json.dumps(user_dict))

	def get(self, id=None):
		if id:
			try:
				u = ndb.Key(urlsafe=id).get()
				if u.token != self.request.headers['Authorization']:
					self.response.set_status(401)
					self.response.write("NOT Authorized")
				else:	
					u_d = u.to_dict()
					u_d['self'] = "/user/" + id
					self.response.write(json.dumps(u_d))
			except:
				self.response.set_status(404)
				self.response.write("Invalid User ID")
		else:
			self.response.set_status(400)
			self.response.write("User ID is required")

	def patch(self, id=None):
		if id:
			try:
				u = ndb.Key(urlsafe=id).get()
				if u.token != self.request.headers['Authorization']:
					self.response.set_status(401)
					self.response.write("NOT Authorized")
				else:
					user_data = json.loads(self.request.body)
					if 'name' in user_data or 'email' in user_data:
						if 'name' in user_data:
							u.name = user_data['name']
						if 'email' in user_data:
							u.email = user_data['email']
						u.put()
					else:
						self.response.set_status(404)
						self.response.write("name and email can be modified")
			except:
				self.response.set_status(404)
				self.response.write("Invalid User ID")
		else:
			self.response.set_status(400)
			self.response.write("User ID is required")

	def delete(self, id=None):
		if id:
			try:
				u = ndb.Key(urlsafe=id).get()
				if u.token != self.request.headers['Authorization']:
					self.response.set_status(401)
					self.response.write("NOT Authorized")
				else:	
					u = ndb.Key(urlsafe=id).get()
					allTodos = ToDo.query()
					for t in allTodos:
						if t.user_id == u.id:
							t.key.delete()
					u.key.delete()
			except:
				self.response.set_status(404)
				self.response.write("Invalid User ID")
		else:
			self.response.set_status(400)
			self.response.write("User ID is required")


class ToDoHandler(webapp2.RequestHandler):
	def post(self):
		user = User
		user_exists = False
		allUsers = User.query()
		for u in allUsers:
			if u.token == self.request.headers['Authorization']:
				user = u
				user_exists = True
		if user_exists is False:
			self.response.set_status(401)
			self.response.write("Unauthorized")
		else:
			todo_data = json.loads(self.request.body)
			new_todo = ToDo(task=todo_data['task'], completed=False, user_id=user.id, date=str(datetime.date.today()))
			new_todo.put()
			new_todo.id = new_todo.key.urlsafe()
			todo_dict = new_todo.to_dict()
			todo_dict['self'] = '/todo/' + new_todo.key.urlsafe()
			new_todo.put()
			self.response.write(json.dumps(todo_dict))

	def get(self, id=None):
		if id:
			try:
				t = ndb.Key(urlsafe=id).get()
				user = User.query(User.id == t.user_id).get()
				if user.token != self.request.headers['Authorization']:
					self.response.set_status(401)
					self.response.write("Unauthorized")
				else:
					t_d = t.to_dict()
					t_d['self'] = "/todo/" + id
					self.response.write(json.dumps(t_d))
			except:
				self.response.set_status(404)
				self.response.write("Invalid Todo ID")
		else:
			self.response.set_status(400)
			self.response.write("Todo ID is required")

	def patch(self, id=None):
		if id:
			try:
				t = ndb.Key(urlsafe=id).get()
				user = User.query(User.id == t.user_id).get()
				if user.token != self.request.headers['Authorization']:
					self.response.set_status(401)
					self.response.write("Unauthorized")
				else:
					todo_data = json.loads(self.request.body)
					if 'task' in todo_data or 'completed' in todo_data:
						if 'task' in todo_data:
							t.task = todo_data['task']
						if 'completed' in todo_data:
							t.completed = todo_data['completed']
						t.put()
					else:
						self.response.set_status(404)
						self.response.write("task and completed can be modified")
			except:
				self.response.set_status(404)
				self.response.write("Invalid Todo ID")
		else:
			self.response.set_status(400)
			self.response.write("ToDo ID is required")

	def delete(self, id=None):	
		if id:
			try:
				t = ndb.Key(urlsafe=id).get()
				user = User.query(User.id == t.user_id).get()
				if user.token != self.request.headers['Authorization']:
					self.response.set_status(401)
					self.response.write("Unauthorized")
				else:
					t.key.delete()
			except:
				self.response.set_status(404)
				self.response.write("Invalid Todo ID")
		else:
			self.response.set_status(400)
			self.response.write("ToDo ID is required")


class UserTodos(webapp2.RequestHandler):
	def get(self, id=None):
		if id:
			try:
				user = User
				user_exists = False
				allUsers = User.query()
				for u in allUsers:
					if u.token == self.request.headers['Authorization']:
						user = u
						user_exists = True
				if user_exists is False:
					self.response.set_status(401)
					self.response.write("Unauthorized")
				else:
					allTodos = ToDo.query()
					toJson = '['
					for t in allTodos:
						if t.user_id == user.id:
							t_d = ndb.Key(urlsafe=t.key.urlsafe()).get().to_dict()
							t_d['self'] = '/todo/' + t.key.urlsafe()
							toJson += str(json.dumps(t_d)) + ','
					toJson = toJson[:-1] 
					toJson += ']'
					self.response.write(toJson)
			except:
				self.response.set_status(404)
				self.response.write("Invalid User ID")
		else:
			self.response.set_status(400)
			self.response.write("User ID is required")


class DeleteAll(webapp2.RequestHandler):
	def delete(self):
		allUsers = User.query()
		for u in allUsers:
			u.key.delete()
		AllToDos = ToDo.query()
		for t in AllToDos:
			t.key.delete()


class AllUsers(webapp2.RequestHandler):
	def get(self):
		user = User
		user_exists = False
		allUsers = User.query()
		for u in allUsers:
			if u.token == self.request.headers['Authorization']:
				user = u
				user_exists = True
		if user_exists is True:			
			allUsers = User.query()
			toJson = '['
			for u in allUsers:
				u_d = ndb.Key(urlsafe=u.key.urlsafe()).get().to_dict()
				u_d['self'] = '/user/' + u.key.urlsafe()
				toJson += str(u_d) + ','			
			toJson = toJson[:-1] 
			toJson += ']'
			self.response.write(toJson)
		else:
			self.response.set_status(401)
			self.response.write("Unauthorized")


class AllToDos(webapp2.RequestHandler):
	def get(self):
		user = User
		user_exists = False
		allUsers = User.query()
		for u in allUsers:
			if u.token == self.request.headers['Authorization']:
				user = u
				user_exists = True
		if user_exists is True:
			allTodos = ToDo.query()
			toJson = '['
			for t in allTodos:
				t_d = ndb.Key(urlsafe=t.key.urlsafe()).get().to_dict()
				t_d['self'] = '/todo/' + t.key.urlsafe()
				toJson += str(json.dumps(t_d)) + ','			
			toJson = toJson[:-1] 
			toJson += ']'
			self.response.write(toJson)


class MainHandler(webapp2.RequestHandler):
	def get(self):
		greeting = "<h1>496 FINAL PROJECT <br>by Daniel Olivas</h1>"
		template_vars = {'hello': greeting}
		template = JINJA_ENV.get_template('home.html')
		self.response.out.write(template.render(template_vars))


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/user', UserHandler),
	('/user/([\w|-]*)', UserHandler),
	('/users', AllUsers),
	('/todo', ToDoHandler),
	('/todo/([\w|-]*)', ToDoHandler),
	('/todos', AllToDos),
	('/user/([\w|-]*)/todos', UserTodos),
	('/deleteall', DeleteAll)
], debug=True)