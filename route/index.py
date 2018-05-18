# -*- coding: UTF-8 -*-

from flask    import *
from os       import environ
from datetime import datetime

from inc.utils  import *
from inc.models import *

from jinja2 import Environment, BaseLoader

from __init__ import __version__

index_page = Blueprint('index', __name__, template_folder='templates')

@index_page.route('/', methods=['GET','POST'] )
def homepage():
  logged_in = is_logged_in() 
  if not logged_in :
    return redirect(url_for('auth.auth'))

  stages = Stages.select()

  if request.method == 'GET' :
    return render_template('index.html', __version__ = __version__, logged_in = logged_in, stages = stages  )


