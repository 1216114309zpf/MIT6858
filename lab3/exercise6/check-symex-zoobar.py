#!/usr/bin/env python2

verbose = True

import symex.fuzzy as fuzzy
import __builtin__
import inspect
import symex.importwrapper as importwrapper
import symex.rewriter as rewriter

importwrapper.rewrite_imports(rewriter.rewriter)

import symex.symflask
import symex.symsql
import symex.symeval
import zoobar

def startresp(status, headers):
  if verbose:
    print 'startresp', status, headers

def report_balance_mismatch():
  print "WARNING: Balance mismatch detected"

def report_zoobar_theft():
  print "WARNING: Zoobar theft detected"

def adduser(pdb, username, token):
  u = zoobar.zoodb.Person()
  u.username = username
  u.token = token
  pdb.add(u)

def test_stuff():
  pdb = zoobar.zoodb.person_setup()
  pdb.query(zoobar.zoodb.Person).delete()
  adduser(pdb, 'alice', 'atok')
  adduser(pdb, 'bob', 'btok')
  zoobars_before = {p.username:p.zoobars for p in pdb.query(zoobar.zoodb.Person).all()}
  balance_before = sum([p.zoobars for p in pdb.query(zoobar.zoodb.Person).all()])
  people_before = sum([1 for p in pdb.query(zoobar.zoodb.Person).all()])
  pdb.commit()

  tdb = zoobar.zoodb.transfer_setup()
  tdb.query(zoobar.zoodb.Transfer).delete()
  tdb.commit()

  environ = {}
  environ['wsgi.url_scheme'] = 'http'
  environ['wsgi.input'] = 'xxx'
  environ['SERVER_NAME'] = 'zoobar'
  environ['SERVER_PORT'] = '80'
  environ['SCRIPT_NAME'] = 'script'
  environ['QUERY_STRING'] = 'query'
  environ['HTTP_REFERER'] = fuzzy.mk_str('referrer')
  environ['HTTP_COOKIE'] = fuzzy.mk_str('cookie')

  ## In two cases, we over-restrict the inputs in order to reduce the
  ## number of paths that "make check" explores, so that it finishes
  ## in a reasonable amount of time.  You could pass unconstrained
  ## concolic values for both REQUEST_METHOD and PATH_INFO, but then
  ## zoobar generates around 2000 distinct paths, and that takes many
  ## minutes to check.

  # environ['REQUEST_METHOD'] = fuzzy.mk_str('method')
  # environ['PATH_INFO'] = fuzzy.mk_str('path')
  environ['REQUEST_METHOD'] = 'GET'
  environ['PATH_INFO'] = 'trans' + fuzzy.mk_str('path')

  if environ['PATH_INFO'].startswith('//'):
    ## Don't bother trying to construct paths with lots of slashes;
    ## otherwise, the lstrip() code generates lots of paths..
    return

  resp = zoobar.app(environ, startresp)
  if verbose:
    for x in resp:
      print x

  ## Exercise 6: your code here.

  ## Detect balance mismatch.
  ## When detected, call report_balance_mismatch()

  #if count of users doesn't change, totoal balance should not change
  zoobars_after = {p.username:p.zoobars for p in pdb.query(zoobar.zoodb.Person).all()}
  balance_after = sum([p.zoobars for p in pdb.query(zoobar.zoodb.Person).all()])
  people_after = sum([1 for p in pdb.query(zoobar.zoodb.Person).all()])
  if people_before == people_after and \
          set(zoobars_before.keys()) == set(zoobars_after.keys()) and \
             balance_before != balance_after:
     report_balance_mismatch()

  ## Detect zoobar theft.
  ## When detected, call report_zoobar_theft()

  # if a user does not request a zoobar transfer, its zoobars should not shrink

  #get all users who request zoobar transfer in this test
  senders = set()
  for transfer in tdb.query(zoobar.zoodb.Transfer).all():
      senders.add(transfer.sender)
  
  for people in pdb.query(zoobar.zoodb.Person).all():
      if people.username not in senders and \
         people.username in zoobars_before and \
         people.username in zoobars_after and \
         zoobars_before[people.username] > zoobars_after[people.username]:
              report_zoobar_theft()

fuzzy.concolic_test(test_stuff, maxiter=2000, verbose=1)

