# -*- coding: UTF-8 -*-

from flask    import *
from os       import environ
from datetime import datetime

from inc.utils  import *
from inc.models import *

from __init__ import __version__

tasks_page = Blueprint('tasks', __name__, template_folder='templates')

@tasks_page.route('/tasks', methods=['GET'] )
@tasks_page.route('/tasks/<page_num>', methods=['GET'] )
def tasks(page_num=1):
  logged_in = is_logged_in() 
  if not logged_in :
    return redirect(url_for('auth.auth'))

  try :
    # try to convert to integer, if not => redirect
    page_num = int(page_num)
  except :
    return redirect(url_for('tasks.tasks'))

  # page must be more or equal 1
  if page_num < 1 :
    return redirect(url_for('tasks.tasks'))

  tasks = Jobs.select().order_by(Jobs.timestamp.desc(), Jobs.id.desc()).paginate(page_num,20)
  stages = Stages.select()

  return render_template( 'admin_tasks.html',  
                          __version__   = __version__, 
                          logged_in     = logged_in,
                          page          = '/tasks', 
                          stages        = stages,
                          tasks         = tasks, 
                          page_num      = page_num )


