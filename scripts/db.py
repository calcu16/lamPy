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
from .pypp import preprocess
from ast import literal_eval

class AbstractConnection(object):
  def __init__(self, **kwargs):
    pass
  def strbuilder(self):
    result = ""
    def builder(s = None):
      nonlocal result
      if s is not None:
        result = "%s%s\n" % (result, s)
      return result
    return builder
  def cursor(self):
    pass
  def execute(self, queryfile, qargs={}, ppargs={}):
    global literal_eval, preprocess
    if isinstance(ppargs, str):
      try:
        ppargs = literal_eval(ppargs)
      except:
        pass
    if isinstance(qargs, str):
      try:
        qargs = literal_eval(qargs)
      except:
        pass
    result = self.strbuilder()
    preprocess('sql/%s.sql' % queryfile, ppargs, result)
    querystr = result()
    self.cur.execute(querystr, qargs)
  def query(self, queryfile, qargs={}, ppargs={}):
    self.execute(queryfile, qargs, ppargs)
    return self.cur.fetchall()
  def queryRow(self, queryfile, qargs={}, ppargs={}):
    self.execute(queryfile, qargs, ppargs)
    return self.cur.fetchone()
  def queryScalar(self, queryfile, qargs={}, ppargs={}):
    row = self.queryRow(queryfile, qargs, ppargs)
    try:
      return next(iter(row.values()))
    except StopIteration:
      return None

def sqlite(**kwargs):
  from sqlite3 import connect

  def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
    return d

  class Connection(AbstractConnection):
    def __init__(self,**kwargs):
      nonlocal dict_factory
      super().__init__(**kwargs)
      self.conn = connect(**kwargs)
      self.cur = self.conn.cursor()
      self.cur.row_factory = dict_factory
  return Connection(**kwargs)

def mysql(**kwargs):
  from .pymysql import connect
  from .pymysql.cursors import DictCursor

  class Connection(AbstractConnection):
    def __init__(self,**kwargs):
      self.conn = connect(cursorclass=DictCursor,**kwargs)
      self.cur = self.conn.cursor()
    def __del__(self):
      self.cur.close()
      self.conn.commit()
      self.conn.close()
  return Connection(**kwargs)

def noSource(**kwargs):
  class Connection(object):
    def __init__(self, **kwargs):
      self.execute = None
      self.query = None
      self.queryRow = None
      self.queryScalar = None
  return Connection(**kwargs)
      
def sql(source, **kwargs):
  sources = {
    'mysql' : mysql,
    'sqlite' : sqlite,
    'none' : noSource
  }
  return sources[source](**kwargs)

