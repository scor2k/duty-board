# -*- coding: UTF-8 -*-

from flask    import *
from os       import environ
from datetime import datetime

from inc.utils  import *
from inc.models import *

from __init__ import __version__, GITLAB_TOKEN

import re

exec_pages = Blueprint('exec', __name__, template_folder='templates')

@exec_pages.route('/exec/<stage>/<int:prj_id>', methods=['GET','POST'] )
def exec_project(stage, prj_id):
  logged_in = is_logged_in() 
  if not logged_in :
    return redirect(url_for('auth.auth'))



  stg_list = Stages.select()
  
  project = Projects.get( Projects.id == prj_id )

  message = "Default Message"
  jobs = []


  if project :
    try :
      pp = Params.select().where( 
                                    (Params.project_id == prj_id) & 
                                    (  
                                      (Params.stage_id == Stages.get( Stages.name == stage.upper() ).id) | 
                                      (Params.stage_id == Stages.get( Stages.name == 'ALL' ).id)            
                                    )
                                  ).execute()

    except Exception as e :
      print("""[%s][ERROR][EXEC][GET] %s""" % ( datetime.now(), e ) )
      pp = Params.select().where( Params.project_id == prj_id, Params.stage_id == Stages.get( Stages.name == stage.upper() ).id ).execute()

  else :
    pp = None

  if request.method == 'POST' :
    form_data = request.form

    if 'exec_project' in form_data :
      # somebody click on button
      try :
        pp = Params.select().where( 
                                    (Params.project_id == prj_id) & 
                                    (  
                                      (Params.stage_id == Stages.get( Stages.name == stage.upper() ).id) | 
                                      (Params.stage_id == Stages.get( Stages.name == 'ALL' ).id)            
                                    )
                                  ).execute()
      except Exception as e:
        print("""[%s][ERROR][EXEC][POST] %s""" % ( datetime.now(), e ) )
        pp = Params.select().where( Params.project_id == prj_id, Params.stage_id == Stages.get( Stages.name == stage.upper() ).id ).execute()


      # replace old value for new

      new_pp = list()

      for p in pp :
        tmp = AttrDict()

        tmp.ask_user = p.ask_user
        tmp.name     = p.name
        tmp.type     = p.type
        tmp.value = p.value

        if p.ask_user == True :
          tmp.value = form_data.get( p.name )

        new_pp.append( tmp )

      # try to generate CURL string
      curl = """curl -X POST \\\r\n"""
      project_id = None
      git_url = None

      request_params = AttrDict() 

      if new_pp :
        for p in new_pp :
          if p.type == 'project_id' :
            project_id = p.value.strip()

          if p.type == 'url' :
            git_url = p.value.strip()

          if p.type == 'ref' :
            curl = curl + """\t-F "ref=%s" \\\r\n""" % p.value.strip()
            request_params.ref = p.value.strip()

          if p.type == 'token' :
            curl = curl + """\t-F "token=%s" \\\r\n""" % p.value.strip()
            request_params.token = p.value.strip()

          if p.type == 'variable' :
            curl = curl + """\t-F "variables[%s]=%s" \\\r\n""" % ( p.name.strip(), p.value.strip() )
            request_params['variables[' + p.name.strip() + ']'] = p.value.strip()

        curl = curl + """\t%s/%s/trigger/pipeline""" % (git_url, project_id)

      # convert params from our class to dict
      json_params = {}
      for rp in request_params:
        json_params[rp] = request_params[rp]

      # log start
      msg = """IP: %s, EXEC on [%s] stage Project [%s] """ % ( request.remote_addr, stage, Projects.get(Projects.id == prj_id).name )
      log_action(session['username'], 'EXEC', msg)
      # log end 

      # log start
      msg = """CURL: %s""" % ( curl )
      log_action(session['username'], 'EXEC CURL', msg)
      # log end 

      # send POST request to Gitlab-CI and get response
      headers1 = {}
      url1 = """%s/%s/trigger/pipeline""" % (git_url, project_id)
      res1 = post_json( url1 , headers1, json_params)

      #print ('--------RES1------------------------------')
      #print (res1)
      #print ('--------RES1------------------------------')

      job_id = None

      if 'error' in res1 :
        message = res1['error']

      if 'id' in res1 :
        pipline_id = res1['id']

        headers2 = {
          "PRIVATE-TOKEN" : GITLAB_TOKEN
        }
        url2 = """%s/%s/pipelines/%s/jobs""" % ( git_url, project_id, pipline_id )
        res2 = get_json( url2, headers2 )

        #print ('--------RES2------------------------------')
        #print (res2)
        #print ('--------RES2------------------------------')

        if 'error' in res2 :
          message = res1['error']
        
        ask2 = None

        # check if any jobs exist
        try :
          ask2 = res2[0]
        except Exception as e :
          print("""[%s][ERROR][POST][PIPLINE] %s""" % ( datetime.now(), e ) )
          message = "В запущенном Pipline нет активных задач"

          # log start
          msg = """JOB ERROR: В запущенном Pipline нет активных задач"""
          log_action(session['username'], 'EXEC ERROR', msg)
          # log end 

        # need check all jobs 
        jobs = []

        for job in res2 :
          job_id = None
          job_name = None

          if 'id' in job :
            job_id = job['id']
          if 'name' in job :
            job_name = job['name']
          
          j = {}
          if job_id != None and job_name != None :
            j['id'] = job_id
            j['name'] = job_name
            if job_name.lower().find( stage.lower() ) >= 0 :
              j['active'] = ''
            else :
              j['active'] = 'disabled'

            jobs.append(j)
            
        #print (jobs)

        if len(jobs) > 0 :
          # have one or more jobs
          message = "Задача запущена."

          # log start
          msg = """PIPLINE: %s JOBS: %s""" % ( pipline_id, jobs )
          log_action(session['username'], 'EXEC JOBS', msg)
          # log end 

          for job in res2: 
            # log to job_log
            url_4_job = """/job/%s/%s/%s """ % ( stage.upper(), project_id, job['id'] )
            log_job(session['username'], prj_id, stage, url_4_job)
            # end job_log

        else :
          message = "Не удалось запустить Pipline."


      stages = Stages.select()
      return render_template( 'exec_project.html', 
                          __version__   = __version__, 
                          logged_in     = logged_in, 
                          page          = '/exec/' + stage, 
                          stages        = stages,
                          stage         = stage.upper(),
                          project       = project,
                          params        = new_pp,
                          curl          = curl,
                          msg           = message,
                          jobs          = jobs,
                          project_id    = project_id
                        )



      



  stages = Stages.select()
  return render_template( 'exec_project.html', 
                          __version__   = __version__, 
                          logged_in     = logged_in, 
                          page          = '/exec/' + stage, 
                          stages        = stages,
                          stage         = stage.upper(),
                          project       = project,
                          params        = pp,
                        )



@exec_pages.route('/exec/<stage>', methods=['GET'] )
def show_projects(stage):
  logged_in = is_logged_in() 
  if not logged_in :
    return redirect(url_for('auth.auth'))

  # generate list of projects for this user
  allow_list  = [-1,]

  try :
    allow = Matrix.select().where( 
                                    ( Matrix.user_id == Users.get( Users.name == session['username'] ).id ) &  
                                    ( 
                                      ( Matrix.stage_id == Stages.get( Stages.name == stage.upper() ).id ) | 
                                      ( Matrix.stage_id == Stages.get( Stages.name == 'ALL' ).id ) 
                                    )
                                  ).execute()
    for a in allow :
      allow_list.append( a.project_id )

  except Exception as e :
    print("""[%s][ERROR][ACCESS] %s""" % ( datetime.now(), e ) )

  # select all projects

  projects = Projects.select().execute()

  stages = Stages.select()

  print("""[%s][DEBUG][ALLOW_LIST] %s""" % ( datetime.now(), allow_list ) )
  p_list = []
  for p in projects:
    p_list.append( p.id )
  print("""[%s][DEBUG][PROJECTS_LIST] %s""" % ( datetime.now(), p_list ) )

  return render_template( 'show_projects.html', 
                          __version__   = __version__, 
                          logged_in     = logged_in, 
                          page          = '/exec/' + stage, 
                          stages        = stages,
                          projects      = projects,
                          stage         = stage,
                          allow         = allow_list
                        )




