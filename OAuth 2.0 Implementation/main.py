# Daniel Olivas
# CS 496
# 2/11/18
# OAuth 2.0 Implementation

import json
import jinja2
import os
import random
import string
import urllib
import webapp2
from google.appengine.api import urlfetch

#https://youtu.be/Unl0dZ6p2xw -- tutorial for jinja2
JINJA_ENV = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + "/template"))

CLIENT_ID = "32593018719-bi4vcq1jdmt7r112c18ff0n6k4csegn4.apps.googleusercontent.com"
CLIENT_SECRET = "NN1DZFfOgjgiy66srMap2vDl"
REDIRECT_URL = "https://olivasd-oauth2.appspot.com/oauth"
#https://pythontips.com/2013/07/28/generating-a-random-string/-- create a random string of letters & numbers
STATE = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])

class MainHandler(webapp2.RequestHandler):
	def get(self):
		url = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=" + CLIENT_ID + \
		"&redirect_uri=" + REDIRECT_URL + "&scope=email&state=" + STATE

		template_vars = {'url': url}
		template = JINJA_ENV.get_template('home.html')
		self.response.out.write(template.render(template_vars))


class OAuthHandler(webapp2.RequestHandler):
	def get(self):
		access_code = self.request.get('code')
		state = self.request.get('state')
		header = {'Content-Type': 'application/x-www-form-urlencoded'}
		payload = {
			'code': access_code,
			'client_id': CLIENT_ID,
			'client_secret': CLIENT_SECRET,
			'redirect_uri': REDIRECT_URL,
			'grant_type': 'authorization_code'
		}
		payload = urllib.urlencode(payload)
		result = urlfetch.fetch(url="https://www.googleapis.com/oauth2/v4/token", payload=payload, headers=header, method=urlfetch.POST)

		results = json.loads(result.content)

		header = {'authorization': 'Bearer ' + results['access_token']}

		result = urlfetch.fetch(url="https://www.googleapis.com/plus/v1/people/me", headers=header, method=urlfetch.GET)
		results = json.loads(result.content)

		template_vars = {'first': results['name']['givenName'], "last": results['name']['familyName'], 
			'url': results['url'], 'state': STATE, 'display_name': results['displayName']}
		template = JINJA_ENV.get_template('oauth.html')
		self.response.out.write(template.render(template_vars))	



allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/oauth', OAuthHandler)
], debug=True)