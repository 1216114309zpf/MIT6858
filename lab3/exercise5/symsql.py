## This module wraps SQLalchemy's methods to be friendly to
## symbolic / concolic execution.

import fuzzy
import sqlalchemy.orm

oldget = sqlalchemy.orm.query.Query.get
def newget(query, primary_key):
  ## Exercise 5: your code here.
  ##
  ## Find the object with the primary key "primary_key" in SQLalchemy
  ## query object "query", and do so in a symbolic-friendly way.
  ##
  ## Hint: given a SQLalchemy row object r, you can find the name of
  ## its primary key using r.__table__.primary_key.columns.keys()[0]

  #here we must use getattr(obj,obj.__table__.primary_key.columns.keys()[0]) instead of
  #  obj.__table__.primary_key.columns.keys()[0]
  #  because obj.__table__.primary_key.columns.keys()[0] is just the key name not the value
  for obj in query.all():
     if primary_key ==  getattr(obj,obj.__table__.primary_key.columns.keys()[0]):
         return obj
  return None

sqlalchemy.orm.query.Query.get = newget
