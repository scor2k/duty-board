# -*- coding: UTF-8 -*-

from flask    import *
from datetime   import datetime
from os       import environ

from __init__   import __version__

from inc.ldap   import LdapUsers
from inc.models import *
from inc.utils  import *

auth_page = Blueprint('auth', __name__, template_folder='templates')


@auth_page.route('/auth', methods=['GET', 'POST'] )
def auth():
  auth = {}

  if request.method == 'POST' :
    u = LdapUsers()

    username  = request.form.get("user_login")
    passwd    = request.form.get("user_password") 

    print ("""[%s][DEBUG] USERNAME: %s""" % (datetime.now(), username ) )

    #chk_user_result = u.check_user_v2( username, passwd )
    chk_user_result = u.check_user_v3( username, passwd )

    if ( chk_user_result == 200 ) :
      print ("""[%s][INFO] Login Success for user [%s] """ % (datetime.now(), username ) )
      auth['msg']   = """Успешная авторизация."""
      auth['state'] = True
      # save session
      sid = Users.get(Users.name == username ).sid 

      session['username'] = username
      session['sid'] = sid
      
      msg = """IP: %s""" % ( request.remote_addr )
      log_action(session['username'], 'LOGIN', msg )
      return redirect(url_for('index.homepage'))


    if ( chk_user_result == 401 ) :
      # log start
      msg = """IP: %s, USER: %s """ % ( request.remote_addr, username )
      log_action('Anonymous', 'LOGIN FAIL', msg )
      # log end
      print ("""[%s][INFO] Login or password incorrect for user [%s] """ % ( datetime.now(), username ) )
      auth['msg']   = """Неверное имя пользователя или пароля"""
      auth['state'] = False

    if ( chk_user_result == 503 ) :
      print ("""[%s][ERROR] Server side problem with [%s] """ % ( datetime.now(), username ) )
      auth['msg']   = """Ошибка при попытке авторизации."""
      auth['state'] = False


  return render_template('auth.html', __version__ = __version__, page = request.url_rule.rule, auth = auth )

