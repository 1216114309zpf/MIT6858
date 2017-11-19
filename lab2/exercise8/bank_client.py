from debug import *
from zoodb import *
import rpclib


def transfer(sender,recipient,zoobars,token):
    ## Fill in code here.
    with rpclib.client_connect('/banksvc/sock') as c:
        kwargs = {"sender": sender,"recipient": recipient,"zoobars":zoobars,"token":token}
        ret = c.call('transfer',**kwargs)
        return ret

def balance(username):
    ## Fill in code here.
    with rpclib.client_connect('/banksvc/sock') as c:
        kwargs = {"username": username}
        ret = c.call('balance',**kwargs)
        return ret
    
def addaccount(username):
    with rpclib.client_connect('/banksvc/sock') as c:
        kwargs = {"username":username}
        ret = c.call('addaccount',**kwargs)
        return ret

def setuptransferdb():
    with rpclib.client_connect('/banksvc/sock') as c:
        kwargs = {"nothing":2}
        ret = c.call('setuptransferdb',**kwargs)
        return ret

#def get_log(username):
 #   with rpclib.client_connect('/banksvc/sock') as c:
  #      kwargs = {"username":username}
   #     ret = c.call('get_log',**kwargs)
    #    return ret
