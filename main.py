# -*- coding: UTF-8 -*-

import json

from flask      import *
from os         import environ
from datetime   import datetime

from __init__   import __version__

from inc.models import *
from inc.utils  import *

# some settings for Flask
SECRET_KEY  = environ.get('DUTY_FLASK_SECRET_KEY', 'OB3j9Y41AX5L2Its7pDdkqyhHNyYFCWSEIgcI')
DEBUG       = environ.get('DUBY_FLASK_DEBUG', 'True')

app = Flask(__name__)
# register external pages 

############################################## / -> main page
from route.index      import index_page
app.register_blueprint(index_page)
############################################## /auth
from route.auth       import auth_page
app.register_blueprint(auth_page)
############################################## /admin/...
from route.admin      import admin_pages
app.register_blueprint(admin_pages)
############################################## /admin/...
from route.exec       import exec_pages
app.register_blueprint(exec_pages)
############################################## /job/<job_id>
from route.job        import job_page
app.register_blueprint(job_page)
############################################## /logs
from route.logs       import logs_page
app.register_blueprint(logs_page)
############################################## /logs
from route.tasks      import tasks_page
app.register_blueprint(tasks_page)


############################################## /logout
@app.route('/logout', methods=['GET'] )
def logout():
  # log start
  msg = """IP: %s""" % ( request.remote_addr ) 
  log_action(session['username'], 'LOGOUT', msg )
  # log end
  session.pop('username', None)
  session.pop('sid', None)
  return redirect( url_for('index.homepage') )


# other settings
app.secret_key = SECRET_KEY
app.config.from_object(__name__)

init_db()
print ("""[%s][INFO] DB initialization completed""" % datetime.now() )
print ("""[%s][INFO] Duty Board started. Version: %s """ % (datetime.now(),  __version__) )


@app.before_request
def before_request() :
  try :
    pg_sql.connect()
  except Exception as e :
    print ("""[%s][DEBUG][BEFORE] before request. Exception while connect to DB. [%s].""" % ( datetime.now(), e ) )

@app.after_request
def after_request(response) :
  try :
    pg_sql.close()
  except Exception as e :
    print ("""[%s][DEBUG][AFTER] after request. Exception while close DB connection. [%s].""" % ( datetime.now(), e ) )
  return response
 

