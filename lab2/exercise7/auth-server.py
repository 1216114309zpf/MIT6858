#!/usr/bin/env python2

from zoodb import *

import hashlib
import random
import os
import pbkdf2

import rpclib
import sys
from debug import *
import bank_client

class AuthRpcServer(rpclib.RpcServer):
     def newtoken(self,db, cred):
         hashinput = "%s%.10f" % (cred.password, random.random())
         cred.token = hashlib.md5(hashinput).hexdigest()
         db.commit()
         return cred.token
     def rpc_login(self,**kwargs):
         username,password = kwargs["username"], kwargs["password"]
         db = cred_setup()
         cred = db.query(Cred).get(username)
         if not cred:
             return None
         hashvalue = pbkdf2.PBKDF2(password, cred.salt).hexread(32)
         if cred.password == hashvalue:
             return self.newtoken(db, cred)
         else:
             return None
     def rpc_register(self,**kwargs):
         username,password = kwargs["username"], kwargs["password"]
         db = cred_setup()
         cred = db.query(Cred).get(username)
         if cred:
             return None
         newcred = Cred()
         newcred.username = username
         newcred.salt = os.urandom(16)
         newcred.password = pbkdf2.PBKDF2(password, newcred.salt).hexread(32)
         db.add(newcred)
         db.commit()

         #do not forget to update person database and make sure it has the priviledge
         database = person_setup() 
         newperson = Person()
         newperson.username = username
         database.add(newperson)
         database.commit()

         bank_client.addaccount(username)

         return self.newtoken(db, newcred)

     def rpc_check_token(self,**kwargs):
         username,token = kwargs["username"], kwargs["token"]
         db = cred_setup()
         cred = db.query(Cred).get(username)
         if cred and cred.token == token:
             return True
         else:
             return False

(_, dummy_zookld_fd, sockpath) = sys.argv


reload(sys)  
sys.setdefaultencoding('utf8') 

s = AuthRpcServer()
s.run_sockpath_fork(sockpath)
