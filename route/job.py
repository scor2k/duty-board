# -*- coding: UTF-8 -*-

from flask      import *
from os         import environ
from datetime   import datetime

from __init__   import __version__, GITLAB_TOKEN, GITLAB_URL

from inc.utils  import *
from inc.models import *

from ansi2html  import Ansi2HTMLConverter

job_page = Blueprint('job', __name__, template_folder='templates')

@job_page.route('/job/<stage>/<int:project_id>/<int:job_id>', methods=['GET'] )
def job(stage,project_id,job_id):
    # try to get info for selected job id
    headers = {
      "PRIVATE-TOKEN" : GITLAB_TOKEN
    }

    try :
      gitlab_url = Params.get( Params.type == 'url', Params.stage_id == Stages.get( Stages.name == stage ).id ).value
    except Exception as e:
      print("""[%s][ERROR] URL not found in local stage.""" % ( datetime.now() ) )
      gitlab_url = GITLAB_URL

    try :
      gitlab_url = Params.get( Params.type == 'url', Params.stage_id == Stages.get( Stages.name == 'ALL' ).id ).value
    except Exception as e:
      print("""[%s][ERROR] URL not found in global stage ALL.""" % ( datetime.now() ) )
      gitlab_url = GITLAB_URL


    url1 = """%s/%s/jobs/%s/trace""" % ( gitlab_url, project_id, job_id )
    print("""[%s][DEBUG] %s""" % ( datetime.now(), url1 ) )

    ask = get_text( url1, headers )

    ask_revert = []

    for line in ask.splitlines() :
      ask_revert.insert(0, line)

    ask2 = "\r\n".join(ask_revert)

    conv = Ansi2HTMLConverter()
    job_html = conv.convert(ask2)

    return render_template('job.html', __version__ = __version__ , job = job_html, job_id = job_id, project_id = project_id )



