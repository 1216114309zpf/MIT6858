#!/usr/bin/env python2
#
# Insert bank server code here.
#
from zoodb import *


import time

import hashlib
import random
import os
import pbkdf2

import rpclib
import sys
from debug import *

import auth_client

class BankRpcServer(rpclib.RpcServer):
     def rpc_transfer(self,**kwargs):
         sender,recipient,zoobars, token = kwargs["sender"], kwargs["recipient"], kwargs["zoobars"], kwargs["token"]
         if not auth_client.check_token(sender,token):
             return False
         bankdb = bank_setup()
         senderp = bankdb.query(Bank).get(sender)
         recipientp = bankdb.query(Bank).get(recipient)

         sender_balance = senderp.zoobars - zoobars
         recipient_balance = recipientp.zoobars + zoobars

         if sender_balance < 0 or recipient_balance < 0:
             raise ValueError()

         senderp.zoobars = sender_balance
         recipientp.zoobars = recipient_balance
         bankdb.commit()

         transfer = Transfer()
         transfer.sender = sender
         transfer.recipient = recipient
         transfer.amount = zoobars
         transfer.time = time.asctime()

         transferdb = transfer_setup()
         transferdb.add(transfer)
         transferdb.commit()
         return True

     def rpc_balance(self,**kwargs):
         username = kwargs["username"]
         db = bank_setup()
         bank = db.query(Bank).get(username)
         return bank.zoobars

     def rpc_addaccount(self,**kwargs):
         username = kwargs["username"]
         database = bank_setup()
         newaccount = Bank()
         newaccount.username = username
         database.add(newaccount)
         database.commit()
         return None

     def rpc_setuptransferdb(self,**kwargs):
         transferdb = transfer_setup()
         return None

#     def rpc_get_log(self,**kwargs):
 #        username = kwargs["username"]
  #       db = transfer_setup()
   #      return db.query(Transfer).filter(or_(Transfer.sender==username,
    #                                     Transfer.recipient==username))

(_, dummy_zookld_fd, sockpath) = sys.argv


s = BankRpcServer()
s.run_sockpath_fork(sockpath)

