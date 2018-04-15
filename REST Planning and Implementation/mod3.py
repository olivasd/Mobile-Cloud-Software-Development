# Daniel Olivas
# CS 496
# 2/4/18
# REST Planning and Implementation

from google.appengine.ext import ndb
import webapp2
import json

class Boat(ndb.Model):
	id = ndb.StringProperty()
	name = ndb.StringProperty(required=True)
	type = ndb.StringProperty(required=True)
	length = ndb.IntegerProperty(required=True)
	at_sea = ndb.BooleanProperty(required=True)

class BoatHandler(webapp2.RequestHandler):
    #Creates boat, requires name, type, and length
	def post(self):
		boat_data = json.loads(self.request.body)
		if boat_data.get('name') == None or boat_data.get('type') == None or boat_data.get('length') == None:
			self.response.set_status(400)
			self.response.write("name, type, and length are required")
		else:
			new_boat = Boat(name=boat_data['name'], type=boat_data['type'], length=boat_data['length'], at_sea=True) #at_sea by default
			new_boat.put()
			new_boat.id = new_boat.key.urlsafe()
			boat_dict = new_boat.to_dict()
			boat_dict['self'] = '/boat/' + new_boat.key.urlsafe() #self reverensing
			new_boat.put()
			self.response.write(json.dumps(boat_dict))
    
    #returns boat by id or error status
	def get(self, id=None):
		if id:
			try:
				b = ndb.Key(urlsafe=id).get()
				b_d = b.to_dict()
				b_d['self'] = "/boat/" + id
				self.response.write(json.dumps(b_d))
			except:
				self.response.set_status(404)
				self.response.write("Invalid Boat ID")
		else:
			self.response.set_status(400)
			self.response.write("Boat ID is required")

    #deletes boat by id
	def delete(self, id=None):
		if id:
			try:
				b = ndb.Key(urlsafe=id).get()
                #if assiged to slip, slip's current_boat & arrival_date set to None
				if b.at_sea == False:
					s = Slip.query(Slip.current_boat == b.id).get()
					s.current_boat = None
					s.arrival_date = None
					s.put()
				b.key.delete()
			except:
				self.response.set_status(404) #bad id
				self.response.write("Invalid Boat ID")
		else:
			self.response.set_status(400)  #no id
			self.response.write("Boat ID is required")		

	#edits name, and/or type, and/or length, and/or at_sea
    #at_sea only works if in slip and being set to sea. Sets slip's current_boat and 
    #             arrival_date to None
	def patch(self, id=None):
		if id:
			try:
				b = ndb.Key(urlsafe=id).get()
				boat_data = json.loads(self.request.body)
				if 'name' in boat_data or 'type' in boat_data or 'length' in boat_data:
					if 'name' in boat_data:
						b.name = boat_data['name']
					if 'type' in boat_data:
						b.type = boat_data["type"]
					if 'length' in boat_data:
						b.length = boat_data["length"]
					if 'at_sea' in boat_data:
						if b.at_sea == True:		
							self.response.set_status(404)
							self.response.write("use \"slip/{slipID}/boat\" add boat to slip")
						elif boat_data["at_sea"] == True and b.at_sea == False:
							b.at_sea = boat_data["at_sea"]
							s = Slip.query(Slip.current_boat == b.id).get()
							s.current_boat = None
							s.arrival_date = None
							s.put()
					b.put()
				else:
					self.response.set_status(404)  #invalid values
					self.response.write("name, type, and length can be modified")
			except:
				self.response.set_status(400)  #bad id
				self.response.write("Invalid Boat ID")
		else:
			self.response.set_status(400)  #no id
			self.response.write("Boat ID is required")

#return all boats in json format
class AllBoats(webapp2.RequestHandler):
	def get(self, id=None):
		allBoats = Boat.query()
		toJson = '['
		for b in allBoats:
			b_d = ndb.Key(urlsafe=b.key.urlsafe()).get().to_dict()
			b_d['self'] = '/boat/' + b.key.urlsafe()
			toJson += str(json.dumps(b_d)) + ','			
		toJson = toJson[:-1] 
		toJson += ']'
		self.response.write(toJson)


class Slip(ndb.Model):
	id = ndb.StringProperty()
	number = ndb.IntegerProperty(required=True)
	current_boat = ndb.StringProperty()
	arrival_date = ndb.StringProperty()


class SlipHandler(webapp2.RequestHandler):
    #post creates new slip and assigns given number only
	def post(self):
		slip_data = json.loads(self.request.body)
		if slip_data.get('number') == None: #bad, no number not provided
			self.response.set_status(400)
			self.response.write("number is required")
		else:
			new_slip = Slip(number=slip_data['number'], current_boat=None, arrival_date=None) #current_boat & arrival_date = None
			new_slip.put()
			new_slip.id = new_slip.key.urlsafe()
			slip_dict = new_slip.to_dict()
			slip_dict['self'] = '/slip/' + new_slip.key.urlsafe()
			new_slip.put()
			self.response.write(json.dumps(slip_dict))

    #returns slip by id or error status
	def get(self, id=None):
		if id:
			try:
				s = ndb.Key(urlsafe=id).get()
				s_d = s.to_dict()
				s_d['self'] = "/slip/" + id
				if s.current_boat != None:
					s_d['current_boat_url'] = '/boat/' + s.current_boat
				self.response.write(json.dumps(s_d))
			except:
				self.response.set_status(404)
				self.response.write("Invalid Slip ID")
		else:
			self.response.set_status(400)
			self.response.write("Slip ID is required")

	#Deletes slip. Error code returned if slip id is omitted or incorrect.		
	def delete(self, id=None):
		if id:
			try:
				s = ndb.Key(urlsafe=id).get()
				if s.current_boat != None:
					boat = ndb.Key(urlsafe=s.current_boat).get()
					boat.at_sea = True #sets assigned boat to sea
					boat.put()
				s.key.delete()
			except:
				self.response.set_status(404) #bad id
				self.response.write("Invalid Slip ID")
		else:
			self.response.set_status(400) #no id
			self.response.write("Slip ID is required")

    #edit number of slip only
	def patch(self, id=None):
		if id:
			try:
				s = ndb.Key(urlsafe=id).get()
				slip_data = json.loads(self.request.body)					
				if 'number' in slip_data:
					s.number = slip_data['number']
					s.put()
				else:
					self.response.set_status(404)
					self.response.write("Can only modify slip number")
			except:
				self.response.set_status(400)
				self.response.write("Invalid Slip ID")
		else:
			self.response.set_status(400)
			self.response.write("Slip ID is required")

#this is where the slip and boat merge together. 
class Boats_and_Slips(webapp2.RequestHandler):
	def patch(self, id=None):
		if id:
			try:
				s = ndb.Key(urlsafe=id).get()
				slip_data = json.loads(self.request.body)
				if 'current_boat' not in slip_data or 'arrival_date' not in slip_data:
					self.response.set_status(400)
					self.response.write("arrival_date and current_boat are required")
				else:
					if s.current_boat != None:
						self.response.set_status(403)
						self.response.write("Slip is occupied")
					else:
						boat_flag = False	
						for boat in Boat.query():
							if boat.id == slip_data['current_boat']:
								boat_flag = True
						if boat_flag == False:
							self.response.set_status(404)
							self.response.write("Invalid Boat ID")
						else:
							b = ndb.Key(urlsafe=slip_data['current_boat']).get()
							if b.at_sea == False:
								self.response.set_status(400)
								self.response.write("Boat already in Slip")
							else:
								s.current_boat = slip_data['current_boat']
								s.arrival_date = slip_data['arrival_date']
								b.at_sea = False
								s.put()
								b.put()

			except:
				self.response.set_status(400)
				self.response.write("Invalid Slip ID")

#returns all slips in json format
class AllSlips(webapp2.RequestHandler):
	def get(self, id=None):
		allSlips = Slip.query()
		toJson = '['
		for s in allSlips:
			s_d = ndb.Key(urlsafe=s.key.urlsafe()).get().to_dict()
			s_d['self'] = '/slip/' + s.key.urlsafe()
			toJson += str(json.dumps(s_d)) + ','
		toJson = toJson[:-1] 
		toJson += ']'
		self.response.write(toJson)


class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.write("Daniel Olivas -- REST Planning and Implementation")


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boat', BoatHandler),
    ('/boat/(.*)', BoatHandler),
    ('/boats', AllBoats),
    ('/slip', SlipHandler),
    ('/slip/(.*)', SlipHandler),
    ('/slips', AllSlips),
    ('/slips/(.*)/boat', Boats_and_Slips),
], debug=True)
