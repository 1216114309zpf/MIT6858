#!/usr/bin/env python2

import rpclib
import sys
import os
import sandboxlib
import urllib
import hashlib
import socket
import bank
import zoodb
import bank_client
import string

from debug import *

## Cache packages that the sandboxed code might want to import
import time
import errno

class ProfileAPIServer(rpclib.RpcServer):
    def __init__(self, user, visitor):
        self.user = user
        self.visitor = visitor

        persondb = zoodb.person_setup()
        senderp = persondb.query(zoodb.Person).get(self.user)

        cred_db = zoodb.cred_setup()
        token = cred_db.query(zoodb.Cred).get(senderp.username).token
        self.token = token
        
        os.setresgid(8202,8202,8202)
        os.setresuid(3333,3333,3333)

    def rpc_get_self(self):
        return self.user

    def rpc_get_visitor(self):
        return self.visitor

    def rpc_get_xfers(self, username):
        xfers = []
        for xfer in bank.get_log(username):
            xfers.append({ 'sender': xfer.sender,
                           'recipient': xfer.recipient,
                           'amount': xfer.amount,
                           'time': xfer.time,
                         })
        return xfers

    def rpc_get_user_info(self, username):
        person_db = zoodb.person_setup()
        p = person_db.query(zoodb.Person).get(username)
        if not p:
            return None
        return { 'username': p.username,
                 'profile': p.profile,
                 'zoobars': bank_client.balance(username),
               }

    def rpc_xfer(self, target, zoobars):
        bank_client.transfer(self.user, target, zoobars,self.token)

def run_profile(pcode, profile_api_client):
    globals = {'api': profile_api_client}
    exec pcode in globals

class ProfileServer(rpclib.RpcServer):
    def rpc_run(self, pcode, user, visitor):
        uid = 2222 
        
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)          
        clean_username = ''.join(c for c in user if c in valid_chars)
        userdir = '/tmp/profiles/%s/'%clean_username
        if not os.path.exists(userdir):
            os.mkdir(userdir)
            os.chmod(userdir, 0777)

        (sa, sb) = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        pid = os.fork()
        if pid == 0:
            if os.fork() <= 0:
                sa.close()
                ProfileAPIServer(user, visitor).run_sock(sb)
                sys.exit(0)
            else:
                sys.exit(0)
        sb.close()
        os.waitpid(pid, 0)

        sandbox = sandboxlib.Sandbox(userdir, uid, '/profilesvc/lockfile')
        with rpclib.RpcClient(sa) as profile_api_client:
            return sandbox.run( lambda:run_profile(pcode, profile_api_client))

(_, dummy_zookld_fd, sockpath) = sys.argv

s = ProfileServer()
s.run_sockpath_fork(sockpath)
