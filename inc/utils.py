# -*- coding: UTF-8 -*-

import json, requests, re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from flask        import *
from inc.models   import *

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#######################################################
def get_text(url, headers) :
  """GET request and return JSON response"""
  try:
    r = requests.get(url=url, timeout=3, headers=headers, verify=False)
  except requests.exceptions.RequestException as e:
    print ("""[%s][ERROR][get_text][%s] %s """ % (datetime.now(),url, e) )
    data = "ERROR 1000"
    return data

  if r.status_code == 200 or r.status_code == 201 :
    data = r.text
    return data
  else:
    print ("""[%s][ERROR][get_text][%s] Status code: %s """ % (datetime.now(),url, r.status_code) )
    data = "ERROR 2000"
    return data



#######################################################
def get_json(url, headers) :
  """GET request and return JSON response"""
  try:
    r = requests.get(url=url, timeout=3, headers=headers, verify=False)
  except requests.exceptions.RequestException as e:
    print ("""[%s][ERROR][get_json][%s] %s """ % (datetime.now(),url, e) )
    tmp = """{"error" : "Connection timeout: %s " }""" % (url)
    data = json.loads(tmp)
    return data

  if r.status_code == 200 or r.status_code == 201 :
    data = json.loads(r.text)
    return data
  else:
    print ("""[%s][ERROR][get_json][%s] Status code: %s """ % (datetime.now(),url, r.status_code) )
    tmp = """{"error" : "Error while try to get information from %s" }""" % (url)
    data = json.loads(tmp)
    return data


#######################################################
def post_json(url, headers, params) :
  """POST request and return JSON response"""
  try:
    r = requests.post(url=url, headers=headers, timeout=3, data=params, verify=False)
  except requests.exceptions.RequestException as e:
    print ("""[%s][ERROR][post_json][%s] %s """ % (datetime.now(),url, e) )
    #print ("""[%s][ERROR][post_json] Headers: %s """ % (datetime.now(), headers ) )
    #print ("""[%s][ERROR][post_json] Params: %s """ % (datetime.now(), params ) )
    tmp = """{"error" : "Error while try to get information from %s" }""" % (url)
    data = json.loads(tmp)
    return data

  if r.status_code == 200 or r.status_code == 201 :
    data = json.loads(r.text)
    return data
  else:
    print ("""[%s][ERROR][post_json][%s] Status code: %s """ % (datetime.now(),url, r.status_code) )
    #print ("""[%s][ERROR][post_json] Headers: %s """ % (datetime.now(),url, headers ) )
    #print ("""[%s][ERROR][post_json] Params: %s """ % (datetime.now(),url, params ) )

    tmp = """{"error" : "Error while try to get information from %s" }""" % (url)
    data = json.loads(tmp)
    return data

#######################################################
def is_logged_in() :
  """check if user logged in and sid in db equal sid in session storage"""
  if ('username' in session) and ('sid' in session) :
    try :
      uu      = Users.get(Users.sid == session['sid'])
      uname   = uu.name
      isadmin = uu.admin
    except Exception as e :
      print ("""[%s][ERROR] SID not exist or NOT EQUAL for this username""" % datetime.now() )
      session.pop('username', None)
      session.pop('sid', None)
      return False
      

    if  uname == session['username'] :
      if isadmin :
        return 'admin'
      else :
        return 'user'

    else :
      print ("""[%s][INFO] SID not exist or NOT EQUAL for this username""" % datetime.now() )
      session.pop('username', None)
      session.pop('sid', None)
      return False
  else : 
    print ("""[%s][INFO] SID not exist or NOT EQUAL for this username""" % datetime.now() )
    session.pop('username', None)
    session.pop('sid', None)
    return False

#######################################################
def log_job(author_name, project_id, stage_name, url) :
  """save job task to history"""  
  try :
    """ test """
    log = ( Jobs.insert( author = author_name, project_id = project_id, stage_id = Stages.get( Stages.name == stage_name ).id, job_url = url ) )

    if log.execute() > 0 :
      #("""[%s][LOG] new log event was save """ % ( datetime.now() ) )
      return True
    else :
      print ("""[%s][ERROR] Can not add job logs """ % ( datetime.now() ) )

    

  except Exception as e :
    print ("""[%s][ERROR] %s""" % ( datetime.now(), e ) )

  return True


 

#######################################################
def log_action(author, action, message) :
  """Save history log"""
  try :
    log = (  Logs.insert( author=author, action=action, message=message, timestamp = int(datetime.now().timestamp()) )  )
    if log.execute() > 0 :
      #("""[%s][LOG] new log event was save """ % ( datetime.now() ) )
      return True
    else :
      print ("""[%s][ERROR] Can not add logs """ % ( datetime.now() ) )

      
  except Exception as e :
    print ("""[%s][ERROR] Update log failed for user [%s], action: [%s] with message: [%s]  """ % ( datetime.now(), author, action, message ) )
    print ("""[%s][ERROR] %s""" % ( datetime.now(), e ) )

  return True

#######################################################

class AttrDict(dict):
  """ Scikit Learn's container object                                         
  Dictionary-like object that exposes its keys as attributes.                 
  >>> b = AttrDict(a=1, b=2)                                                     
  >>> b['b']                                                                  
  2                                                                           
  >>> b.b                                                                     
  2                                                                           
  >>> b.c = 6                                                                 
  >>> b['c']                                                                  
  6                                                                           
  """                                                                         

  def __init__(self, **kwargs):                                               
      super(AttrDict, self).__init__(kwargs)                                     

  def __setattr__(self, key, value):                                          
      self[key] = value                                                       

  def __dir__(self):                                                          
      return self.keys()                                                      

  def __getattr__(self, key):                                                 
      try:                                                                    
          return self[key]                                                    
      except KeyError:                                                        
          raise AttributeError(key)                                           

  def __setstate__(self, state):                                              
      pass                       


