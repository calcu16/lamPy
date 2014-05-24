# Copyright (c) 2012 Andrew Carter
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.

def setup():
  from base64 import urlsafe_b64encode, urlsafe_b64decode
  from http.cookies import CookieError, SimpleCookie
  from cgi import FieldStorage
  from datetime import datetime
  from .db import sql
  from decimal import Decimal
  from json import JSONEncoder
  from os import environ, path
  from pickle import dumps, loads, UnpicklingError
  from .pypp import preprocess
  from sys import exit

  class DecimalEncoder(JSONEncoder):
    def default(self, obj):
      nonlocal Decimal, JSONEncoder
      if isinstance(obj, Decimal):
        return str(obj)
      return JSONEncoder.default(self, obj)
  
  global toJSON, toHiddenJSON
  def toJSON(obj):
    nonlocal DecimalEncoder
    return DecimalEncoder().encode(obj)
  def toHiddenJSON(obj):
    nonlocal DecimalEncoder
    return toJSON(obj).replace("&", "&#38;").replace("'", "&39;")

  new_cookies = SimpleCookie()
  form = FieldStorage()
  fields = {}
  moon = datetime(1969, 7, 21, 2, 56)

  try:
    old_cookies = SimpleCookie(environ['HTTP_COOKIE'])
  except (CookieError, KeyError):
    old_cookies = {}
  
  global getCookie, setCookie, deleteCookie
  def getCookie(name):
    nonlocal old_cookies
    try:
        return old_cookies[name].value
    except KeyError:
        return None
  def setCookie(name, value):
    nonlocal new_cookies
    new_cookies[name] = value
    new_cookies[name]['expires'] = '0'
  def deleteCookie(name):
    nonlocal new_cookies, moon
    new_cookies[name] = 'expiring'
    new_cookies[name]['expires'] = moon.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
  
  global getField, containsField, setField, saveFields, loadFields
  def getField(name, one = True):
    nonlocal form, fields
    fields[name] = fields.get(name, form.getfirst(name) if one else form.getlist(name))
    return fields[name]
  def containsField(name):
    nonlocal form, fields
    return name in fields or name in form
  def setField(name, value):
    nonlocal fields
    fields[name] = value
  def saveFields():
    nonlocal fields, urlsafe_b64encode, dumps
    return str(urlsafe_b64encode(dumps(fields,-1)))[2:-1]
  def loadFields(dictionary):
    nonlocal fields, loads, urlsafe_b64decode, UnpicklingError
    try:
      if dictionary:
        fields = loads(urlsafe_b64decode(bytes(dictionary, 'utf-8')))
    except UnpicklingError:
      pass
    
  global redirect, serve, AJAX, error
  def redirect(loc):
    nonlocal new_cookies
    print("Location: %s" % loc)
    print(new_cookies.output(sep = '\n'))
    print()
    exit(0)
  def AJAX(doc):
    global toJSON
    print("Content-type: text/plain")
    print()
    print(toJSON(doc))
    exit(0)
  def serve(name):
    global values, getField
    nonlocal preprocess, new_cookies, path
    values['__COOKIES__'] = new_cookies.output(sep = '\n')
    values['getField'] = getField
    folder = name.rsplit(".", 1)[1]
    try:
      preprocess(path.join(folder, name), values, None, root="./")
    except IOError as e:
      if e.errno == 2:
        error(name, 404)
      else:
        raise
    preprocess(path.join(folder, name), values, root="./")
    exit(0)
  
  errmessages = {
    404 : 'Not Found'
  }
  def error(name, errno):
    global values
    nonlocal errmessages
    values['__ERRFILE__'] = name
    values['__ERRNO__'] = errno
    values['__ERRMESSAGE__'] = errmessages[errno]
    preprocess(path.join('html', '%d.html' % errno), values)
    exit(0)
  try:
    setField('query_string', '?%s' % environ['QUERY_STRING'])
  except KeyError:
    setField('query_string', '')

  conn = sql(**preprocess('conf/db.conf'))
  
  global values
  values = {
    'query_string' : getField('query_string'),
    'redirect' : '',
    'execute' : conn.execute,
    'query' : conn.query,
    'queryRow' : conn.queryRow,
    'queryScalar' : conn.queryScalar,
  }
  values['site_path'] = path.dirname(environ['SCRIPT_NAME'])
  values['file_path'] = environ['REDIRECT_URL'][len(values['site_path']):]
  if not path.splitext(values['file_path'])[1]:
    values['file_path'] = path.join(values['file_path'], '')
  values['file_dir'], values['file_name'] = path.split(values['file_path'])
  if not values['file_name']:
    values['file_name'] = 'index.html'
    values['file_path'] = path.join(values['file_dir'],values['file_name'])

