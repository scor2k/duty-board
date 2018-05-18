# -*- coding: UTF-8 -*-
from datetime import datetime
from os       import environ

import binascii
import os
import sys

from ldap3 import Server as ldap_server
from ldap3 import Connection as ldap_connection
from ldap3 import SIMPLE, SYNC, ALL, SUBTREE, ALL_ATTRIBUTES

from inc.models import *


class LdapUsers() :
  LDAP = None

  def __init__(self):
    """Get LDAP variables from env"""
    self.LDAP_SERVER      = environ.get('DUTY_LDAP_SERVER', '')
    self.LDAP_PORT        = environ.get('DUTY_LDAP_PORT', 389)
    self.LDAP_DOMAIN      = environ.get('DUTY_LDAP_DOMAIN', '')
    self.LDAP_BASEDN      = environ.get('DUTY_LDAP_BASEDN', '')
    self.LDAP_GROUPDN     = environ.get('DUTY_LDAP_GROUPDN', '') 
    
    self.LDAP_GROUP_FILTER        = '(&(objectClass=GROUP)(cn={group_name}))'
    self.LDAP_USER_FILTER         = '(&(objectClass=USER)(sAMAccountName={username}))'

    # convert LDAP_PORT to int
    self.LDAP_PORT = int(self.LDAP_PORT)

  def disconnect(self) :
    try :
      self.LDAP.unbind()
    except Exception as e :
      print (e)

  def try_connect(self, username, password) :
    try:
      user_dn = """%s@%s""" % ( username, self.LDAP_DOMAIN )
      ls = ldap_server(self.LDAP_SERVER, self.LDAP_PORT, get_info=ALL)
      self.LDAP = ldap_connection(ls, authentication=SIMPLE, user=user_dn, password=password, check_names=True, lazy=False, client_strategy=SYNC, raise_exceptions=False)
      self.LDAP.bind()

    except Exception as e:
      print ("""[%s][DEBUG] LDAP Exception: %s  """ % (datetime.now(), e ) )
      return False

    return self.LDAP.result

  def check_user_v2(self, username, password) :
    """check user credentials via LDAP version 2"""

    res = self.try_connect( username, password ) 

    print ("""[%s][DEBUG] LDAP Result: %s  """ % (datetime.now(), res) )

    if ( res ) :
      # user password is correct

      if 'description' in res : 
        if res['description'] == 'invalidCredentials' : 
          print ("""[%s][DEBUG] Invalid username or password  """ % (datetime.now() ) )
          # 401 HTTP 
          return 401

        if res['description'] == 'success' :
          self.disconnect()

          sid = binascii.hexlify(os.urandom(16)).decode()
          try :
            ins = Users.insert( name=username, sid = sid ).execute()

            # if insert success => new user. If we have only one user => need to set 'admin' = True
            #print ("""[DEBUG] count : %s """ % Users.select().count() )
            if ( Users.select().count() == 1 ) :
              Users.update( admin = True ).where(Users.name == username).execute() 
          except Exception as e :
            print (e)

            #print ("""[DEBUG] count : %s """ % Users.select().count() )
            upd = Users.update(timestamp=int(datetime.timestamp(datetime.now())), sid = sid ).where(Users.name == username).execute()
          # 200 OK
          return 200

    
    else :
      print ("""[%s][ERROR] LDAP serves is not available """ % (datetime.now() ) )
      # 503 Service Unavailable
      return 503
 
   
  def check_user_v3(self, username, password) :
    """check user credentials via LDAP version 3"""

    res = self.try_connect( username, password ) 

    print ("""[%s][DEBUG] LDAP Result: %s  """ % (datetime.now(), res) )

    if ( res ) :
      # user password is correct

      if 'description' in res : 

        if res['description'] == 'invalidCredentials' : 
          print ("""[%s][DEBUG] Invalid username or password  """ % (datetime.now() ) )

          # 401 HTTP 
          return 401

        elif res['description'] == 'success' :
          self.disconnect()

          sid = binascii.hexlify(os.urandom(16)).decode()

          # by default user not new
          is_new_user = False

          try :
            ins = Users.insert( name=username, sid = sid ).execute()

            # if exception does not work => it's new user 
            is_new_user = True

            #print ("""[DEBUG] count : %s """ % Users.select().count() )
          except Exception as e :
            print ("""[%s][SQL INSERT ERROR] %s """ % (datetime.now(), e) )


          if is_new_user :
            # if insert success => new user. If we have only one user => need to set 'admin' = True
            try :
              if ( Users.select().count() == 1 ) :
                Users.update( admin = True ).where(Users.name == username).execute() 

            except Exception as e :
              print ("""[%s][SQL SET ADMIN ERROR] %s """ % (datetime.now(), e) )

          else:
            # if user not new ->  need update

            try :
              upd = Users.update(timestamp=int(datetime.timestamp(datetime.now())), sid = sid ).where(Users.name == username).execute()

              # 200 ok
              return 200

            except Exception as e :
              print ("""[%s][SQL UPDATE USER ERROR] %s """ % (datetime.now(), e) )
              # return 500 if can not update user
              return 503

        else :
          print ("""[%s][LDAP ERROR] %s """ % (datetime.now(), res) )

        # 500 OK
        return 503
    
    else :
      print ("""[%s][ERROR] LDAP serves is not available """ % (datetime.now() ) )
      # 503 Service Unavailable
      return 503
 
 
