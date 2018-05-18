# -*- coding: UTF-8 -*-

from flask    import *
from os       import environ
from datetime import datetime

from inc.utils  import *
from inc.models import *

from __init__ import __version__

logs_page = Blueprint('logs', __name__, template_folder='templates')

@logs_page.route('/logs', methods=['GET'] )
@logs_page.route('/logs/<page_num>', methods=['GET'] )
def logs(page_num=1):
  logged_in = is_logged_in() 
  if not logged_in :
    return redirect(url_for('auth.auth'))

  try :
    # try to convert to integer, if not => redirect
    page_num = int(page_num)
  except :
    return redirect(url_for('logs.logs'))

  # page must be more or equal 1
  if page_num < 1 :
    return redirect(url_for('logs.logs'))

  logs = Logs.select().order_by(Logs.timestamp.desc(), Logs.id.desc()).paginate(page_num,20)
  stages = Stages.select()

  return render_template( 'admin_logs.html',  
                          __version__   = __version__, 
                          logged_in     = logged_in,
                          page          = '/logs', 
                          stages        = stages,
                          logs          = logs, 
                          page_num      = page_num )


