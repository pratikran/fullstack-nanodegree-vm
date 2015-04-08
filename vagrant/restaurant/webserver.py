from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem
from time import time

class Db():
	def __init__(self):
		self.engine = create_engine('sqlite:///restaurantmenu.db')
		Base.metadata.bind = self.engine
		self.DBSession = sessionmaker(bind=self.engine)

	def makeSession(self):
		self.session = self.DBSession()

	def getSession(self):
		return self.session

	def queryAll(self, tableclass, **filter):
		self.makeSession()
		if filter.get("name") != None and filter.get("id") != None:
			result = self.getSession().query(tableclass).filter_by(name=filter["name"], id=filter["id"]).all()
		elif filter.get("name") != None:
			result = self.getSession().query(tableclass).filter_by(name=filter["name"]).all()
		elif filter.get("id") != None:
			result = self.getSession().query(tableclass).filter_by(id=filter["id"]).all()
		else:
			result = self.getSession().query(tableclass).all()
		return result

	def queryOne(self, tableclass, **filter):
		self.makeSession()
		if filter.get("name") != None and filter.get("id") != None:
			result = self.getSession().query(tableclass).filter_by(name=filter["name"], id=filter["id"]).first()
		elif filter.get("name") != None:
			result = self.getSession().query(tableclass).filter_by(name=filter["name"]).first()
		elif filter.get("id") != None:
			result = self.getSession().query(tableclass).filter_by(id=filter["id"]).first()
		else:
			result = self.getSession().query(tableclass).first()
		return result

	def insertOne(self, tableclass, name=None):
		self.makeSession()

		# name is a list
		if len(name) == 1 and name[0] != None:
			newEntry = tableclass(name = name[0])
			self.getSession().add(newEntry)
			self.getSession().commit()
		else:
			print name+": Not a valid name to insert into "+tableclass.__name__

	def updateOne(self, tableclass, name=None, id=0):
		self.makeSession()

		# name is a list
		if len(name) == 1 and name[0] != None and id > 0:
			existingEntry = self.getSession().query(tableclass).filter_by(id=id).one()
			existingEntry.name = name[0]
			self.getSession().add(existingEntry)
			self.getSession().commit()
		else:
			print id+": Not a valid id to delete from "+tableclass.__name__

	def deleteOne(self, tableclass, id=0):
		self.makeSession()
		if id > 0:
			deleteEntry = self.getSession().query(tableclass).filter_by(id=id).one()
			self.getSession().delete(deleteEntry)
			self.getSession().commit()
		else:
			print id+": Not a valid id to delete from "+tableclass.__name__


class webServerHandler(BaseHTTPRequestHandler):

	def getIdFromUrl(self, urlPath):
		return int(urlPath.split('/')[-2])

	def do_GET(self):
		try:
			if self.path.endswith("/edit"):
				self.send_response(200)
				self.send_header('content-type', 'text/html')
				self.end_headers()
				id = self.getIdFromUrl(self.path)
				filter = {'id':id}
				restaurant_name = self.server.db.queryOne(Restaurant, **filter).name
				output = ""
				output += "<html><body>"
				output += "Hello!"
				output += "<form method='POST' enctype='multipart/form-data' action='"+self.path+"'> \
				            <h2>Edit '"+restaurant_name+"' Restaurant</h2><input name='restaurant' \
				            type='text' ><input type='submit' value='Enter Restaurant&#39;s New Name'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			if self.path.endswith("/delete"):
				self.send_response(200)
				self.send_header('content-type', 'text/html')
				self.end_headers()
				id = self.getIdFromUrl(self.path)
				filter = {'id':id}
				restaurant_name = self.server.db.queryOne(Restaurant, **filter).name
				output = ""
				output += "<html><body>"
				output += "Hello!"
				output += "<form method='POST' enctype='multipart/form-data' action='"+self.path+"'> \
				            <h2>Por Favor, Confirm to delete '"+restaurant_name+"' Restaurant</h2><input type='submit' name='confirm' value='Yes, Delete Restaurant'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			if self.path.endswith("/restaurants"):
				#print time(), "A"
				self.send_response(200)
				self.send_header('content-type', 'text/html')
				self.end_headers()
				self.restaurants = self.server.db.queryAll(Restaurant)
				output = ""
				output += "<html><body>"
				output += "<h1>Hola! Ver la list de restaurantes, por favor.</h1>"
				output += "<ul>"
				for restaurant in self.restaurants:
					output += "<li>"+restaurant.name+"<br><a href='/restaurant/"+str(restaurant.id)+"/edit'>edit</a><br><a href='/restaurant/"+str(restaurant.id)+"/delete'>delete</a><br><br></li>"
				output += "</ul>"
				output += "<div><a href='/restaurants/new'>Make a New Restaurant</a></div></body></html>"
				self.wfile.write(output)
				print output
				#print time(), "B"
				return
			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "Hello!"
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurants'> \
				            <h2>Create a new Restaurant</h2><input name='restaurant' \
				            type='text' ><input type='submit' value='Create Restaurant'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "Hello!"
				output += "<form method='POST' enctype='multipart/form-data' action='/hello'> \
				            <h2>What would you like me to say?</h2><input name='message' \
				            type='text' ><input type='submit' value='Submit'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>&#161Hola <a href='/hello'>Back to Hello</a></body></html>"
				self.wfile.write(output)
				print output
				return
		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)
		else:
			pass
		finally:
			pass

	def do_POST(self):
		try:

			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				fields = cgi.parse_multipart(self.rfile, pdict)

			if self.path.find("/edit") != -1:
				#print time(), "C"
				self.send_response(301)
				#self.send_header('Location','http://localhost:8080/restaurants')
				self.end_headers()

				restaurant_name = fields.get('restaurant')

				id = self.getIdFromUrl(self.path)

				filter = {'id':id}
				restaurant_old_name = self.server.db.queryOne(Restaurant, **filter).name

				self.server.db.updateOne(Restaurant, restaurant_name, id)
				#print restaurant_name
				restaurant_name = self.server.db.queryOne(Restaurant, **filter).name

				output = "<html><body><h1>Restaurant '"+restaurant_old_name+"' Updated to "+restaurant_name+"</h1><a href='/restaurants'>Click here to goto restaurants list</a></body></html>"

			if self.path.find("/delete") != -1:
				#print time(), "C"
				self.send_response(301)
				self.send_header('Location','/restaurants')
				self.end_headers()

				messagecontent = fields.get('confirm')
				if messagecontent[0].lower().find('yes') != -1:
					id = self.getIdFromUrl(self.path)
					filter = {'id':id}
					restaurant_name = self.server.db.queryOne(Restaurant, **filter).name
					#print restaurant_name

					self.server.db.deleteOne(Restaurant, id)
					#print time(), "D"

					output = "<html><body>Deleted "+str(id)+"</body></html>"

			if self.path.find("/restaurants") != -1:
				self.send_response(301)
				self.end_headers()

				messagecontent = fields.get('restaurant')
				self.server.db.insertOne(Restaurant, messagecontent)
				self.restaurants = self.server.db.queryAll(Restaurant)

				output = ""
				output += "<html><body>"
				output += "<h2>Restaurant '%s' added</h2>" % messagecontent[0]
				output += "<h1>Hola! La listes de restaurantes, por favor.</h1>"
				output += "<ul>"
				for restaurant in self.restaurants:
					output += "<li>"+restaurant.name+"<br><a href='/restaurant/"+str(restaurant.id)+"/edit'>edit</a><br><a href='/restaurant/"+str(restaurant.id)+"/delete'>delete</a><br><br></li>"
				output += "</ul>"
				output += "<div><a href='/restaurants/new'>Make a New Restaurant</a></div></body></html>"
			if self.path.find("/hello") != -1:
				self.send_response(301)
				self.end_headers()

				messagecontent = fields.get('message')

				output = ""
				output += "<html><body>"
				output += "<h2> Okay, how about this: </h2>"
				output += "<h1> %s </h1>" % messagecontent[0]
				output += "<form method='POST' enctype='multipart/form-data' action='/hello'> \
					            <h2>What would you like me to say?</h2><input name='message' \
					            type='text' ><input type='submit' value='Submit'></form>"
				output += "</body></html>"

			#print time(), "E"
			self.wfile.write(output)
			print output
			#print time(), "F"

		except Exception, e:
			raise
		else:
			pass
		finally:
			pass


def serveWeb():
	try:
		port = 8080
		server = HTTPServer(('', port), webServerHandler)
		server.db = Db()
		print "Web Server is runnning on port %s" % port
		server.serve_forever()
	except KeyboardInterrupt:
		print " ^C entered, stopping web server....."
		server.socket.close()
	else:
		pass
	finally:
		pass


if __name__ == '__main__':
	serveWeb()
