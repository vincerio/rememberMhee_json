#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import os
from string import letters
import webapp2
import jinja2
import json
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = False)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
		
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
		
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
		
    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

class Tasks(db.Model):
	description = db.StringProperty()
	completed = db.BooleanProperty(default=False)
	
	def as_dict(self):
		d = { 'description':self.description , 'completed':self.completed ,'id':self.key().id()}
		return d

class MainHandler(Handler):
    def get(self):
		self.render('base.html')
	
class TasksHandler(Handler):
	def post(self):
		desc = self.request.get('description')
		t = Tasks(description = desc)
		t.put()
		tid = str(t.key().id())
		self.redirect('/tasks/%s' %tid)
	

	def get(self):
		tasks = Tasks.all()
		return self.render_json([p.as_dict() for p in tasks])

class SingleTaskHandler(Handler):		
	def put(self):
		desc = self.request.get('description')
		com = self.request.get('completed')
		url = self.request.url
		position = url.find('tasks')
		id = url[position+6:]
		task = Tasks.get_by_id(int(id))
		task.description = desc
		task.completed = bool(com)
		task.put()
		return self.render_json(task.as_dict())

	def delete(self):
		url = self.request.url
		position = url.find('tasks')
		id = url[position+6:]
		task = Tasks.get_by_id(int(id))
		task.delete()
		
	def get(self):
		url = self.request.url
		position = url.find('tasks')
		id = url[position+6:]
		task = Tasks.get_by_id(int(id))
		return self.render_json(task.as_dict())
		
								
app = webapp2.WSGIApplication([
    ('/', MainHandler),
	('/tasks', TasksHandler),
	('/tasks/.*', SingleTaskHandler)

	
], debug=True)
