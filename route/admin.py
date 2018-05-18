# -*- coding: UTF-8 -*-

from flask    import *
from os       import environ
from datetime import datetime

from inc.utils  import *
from inc.models import *

from __init__ import __version__

admin_pages = Blueprint('admin', __name__, template_folder='templates')

@admin_pages.route('/admin/matrix', methods=['GET', 'POST'] )
def matrix():
  logged_in = is_logged_in() 
  if not logged_in :
    return redirect(url_for('auth.auth'))

  if logged_in != 'admin' :
    return redirect(url_for('index.homepage'))

  if request.method == 'POST' :
    form_data = request.form

    # click remove button
    if 'remove_matrix_id' in form_data:
      remove_matrix_id = form_data.get('remove_matrix_id')

      # log start
      try :
        mm = Matrix.get( Matrix.id == remove_matrix_id )
        project = mm.project.name
        stage_name = mm.stage.name
        user_name = mm.user.name
      except :
        project = ""
        stage_name = ""
        user_name = ""

      msg = """IP: %s, User: [%s] Stage: [%s] Project: [%s] """ % ( request.remote_addr, user_name, stage_name, project  )
      log_action(session['username'], 'REMOVE MATRIX', msg)
      # log end 

      Matrix.delete().where( Matrix.id == remove_matrix_id ).execute()


    # click add new access
    if 'new_matrix_stage' in form_data:
      new_matrix_stage    = form_data.get('new_matrix_stage')
      new_matrix_user     = form_data.get('new_matrix_user')
      new_matrix_project  = form_data.get('new_matrix_project')

      try :
        Matrix.create( user_id = new_matrix_user, stage_id = new_matrix_stage, project_id = new_matrix_project, access = True )

        # log start
        try :
          project     = Projects.get( id == new_matrix_project ).name
          stage_name  = Stages.get( id == new_matrix_stage ).name
          user_name   = Users.get( id == new_matrix_user ).name
        except :
          project = ""
          stage_name = ""
          user_name = ""

        msg = """IP: %s, User: [%s] Stage: [%s] Project: [%s] """ % ( request.remote_addr, user_name, stage_name, project  )
        log_action(session['username'], 'CREATE MATRIX', msg)
        # log end 

      except Exception as e:
        print("""[%s][ERROR][MATRIX] [%s]""" % (datetime.now(), e ) )



  stg_list    = Stages.select().order_by( Stages.name )
  prj_list    = Projects.select().order_by( Projects.name )
  usr_list    = Users.select().order_by( Users.name )
  matrix_list = Matrix.select().order_by( Matrix.id )

  return render_template( 'admin_matrix.html', 
                          __version__   = __version__, 
                          logged_in     = logged_in, 
                          page          = request.url_rule.rule, 
                          stages        = stg_list, 
                          projects      = prj_list,
                          users         = usr_list,
                          matrix        = matrix_list
                        )


@admin_pages.route('/admin/configure/<int:project_id>', methods=['GET', 'POST'] )
def configure(project_id):
  logged_in = is_logged_in() 
  if not logged_in :
    return redirect(url_for('auth.auth'))

  if logged_in != 'admin' :
    return redirect(url_for('index.homepage'))

  if request.method == 'POST' :
    form_data = request.form

    if 'project_upd_name' in form_data :
      #TODO
      print ('first form')

    if 'remove_param_id' in form_data:
      # click remove button
      remove_param_id = form_data.get('remove_param_id')

      # log start
      # get project name by param_id
      try :
        project = Projects.get( Projects.id == Params.get( Params.id == remove_param_id ).project_id ).name
      except :
        project = ""

      try :
        param_name = Params.get( Params.id == remove_param_id ).name
      except :
        param_name = ""

      try :
        value = Params.get( Params.id == remove_param_id ).value 
      except :
        value = ""

      msg = """IP: %s, Project: [%s] Param [%s] with value [%s] """ % ( request.remote_addr, project, param_name, value  )
      log_action(session['username'], 'REMOVE PARAM', msg)
      # log end 

      Params.delete().where( Params.id == remove_param_id ).execute()


    if 'new_param_name' in form_data :
      project_id          = form_data.get('project_id')

      new_param_stage     = form_data.get('new_param_stage')
      new_param_type      = form_data.get('new_param_type')
      new_param_askuser   = form_data.get('new_param_askuser')
      new_param_name      = form_data.get('new_param_name')
      new_param_value     = form_data.get('new_param_value')

      if new_param_askuser == 'on' :
        new_param_askuser = True
      else :
        new_param_askuser = False

      try :
        print("""[%s][DEBUG] Create new param type [%s] for projectID: [%s]""" % (datetime.now(), new_param_type, project_id ) )

        Params.insert(  project_id   = project_id,
                        stage_id     = Stages.get( Stages.name == new_param_stage ).id,
                        type         = new_param_type,
                        ask_user     = new_param_askuser,
                        name         = new_param_name,
                        value        = new_param_value ).execute()
        # log start
        msg = """IP: %s, TYPE [%s], NAME [%s] for ProjectID [%s] : %s""" % ( request.remote_addr, new_param_type, new_param_name, project_id, new_param_value )
        log_action(session['username'], 'CREATE PARAM', msg)
        # log end 

      except Exception as e :
        print("""[%s][ERROR] While creating new param [%s] for projectID: [%s]""" % (datetime.now(), new_param_name, project_id ) )
        print (e)

      return redirect( url_for('admin.configure', project_id=project_id) )


  stg_list = Stages.select()
  project = Projects.get( Projects.id == project_id )
  if project :
    #pp  = Params.select(Params.project_id == project_id).order_by(Params.stage).execute()
    pp  = Params.select().where( Params.project_id == project_id ).execute()

  else :
    pp = None


  return render_template( 'admin_configure.html', 
                          __version__   = __version__, 
                          logged_in     = logged_in, 
                          page          = '/admin/configure',
                          stages        = stg_list, 
                          project       = project,
                          params        = pp
                        )


@admin_pages.route('/admin/users', methods=['GET', 'POST'] )
def users() :
  logged_in = is_logged_in() 
  if not logged_in :
    return redirect(url_for('auth.auth'))

  if logged_in != 'admin' :
    return redirect(url_for('index.homepage'))

  if request.method == 'POST' :
    data = request.form

    username = None
    is_admin = False

    if 'user' in data :
      username = data['user']

    if 'admin' in data :
      is_admin = True

    if 'username' != None :
      try :
        Users.update( admin = is_admin ).where( Users.name == username ).execute()

        # log start
        msg = """IP: %s, set (True)/unset(False) admin rights [%s] for user [%s] """ % ( request.remote_addr, is_admin, username )
        subj = """CHANGE ADMIN"""
        log_action(session['username'], subj, msg)
        # log end

      except Exception as e :
        print("""[%s][ERROR] [%s]""" % (datetime.now(), e ) )
        
        
      
      


  usr_list = Users.select(Users.id, Users.name, Users.admin, Users.timestamp).order_by(Users.id)
  stg_list = Stages.select()
  return render_template( 'admin_users.html', 
                          __version__ = __version__, 
                          logged_in = logged_in, 
                          page = request.url_rule.rule, 
                          stages  = stg_list,
                          users   = usr_list
                        )


 

@admin_pages.route('/admin/stages', methods=['GET', 'POST'] )
def stages():
  logged_in = is_logged_in() 
  if not logged_in :
    return redirect(url_for('auth.auth'))

  if logged_in != 'admin' :
    return redirect(url_for('index.homepage'))

  if request.method == 'POST' :
    # get new project name
    stg_name = request.form.get('stage_new_name')


    if ( len(stg_name) <= 1 ) :
      stg_list = Stages.select()
      return render_template( 'admin_stages.html', 
                              __version__ = __version__, 
                              logged_in = logged_in, 
                              page = request.url_rule.rule, 
                              stages = stg_list, 
                              msg = "Слишком короткое название среды исполнения" 
                            )

    try :
      Stages.create(name=stg_name)
      print("""[%s][DEBUG] Insert new stage [%s]""" % (datetime.now(), stg_name ) )

      # log start
      msg = """IP: %s, STAGE: %s""" % ( request.remote_addr, stg_name )
      log_action(session['username'], 'NEW STAGE', msg)
      # log end 

      stg_list = Stages.select()

      msg = """Среда исполнения [%s] добавлена""" % stg_name 
      return render_template( 'admin_stages.html', 
                              __version__ = __version__, 
                              logged_in = logged_in, 
                              page = request.url_rule.rule, 
                              stages = stg_list, 
                              msg = msg
                            )


    except Exception as e: 
      print("""[%s][ERROR] [%s]""" % (datetime.now(), e ) )

      msg = """Ошибка при добавлении среды исполнения [%s]""" % stg_name 
      stg_list = Stages.select()
      return render_template( 'admin_stages.html', 
                              __version__ = __version__, 
                              logged_in = logged_in, 
                              page = request.url_rule.rule, 
                              stages = stg_list, 
                              msg = msg
                            )


  stg_list = Stages.select()
  return render_template( 'admin_stages.html', 
                          __version__ = __version__, 
                          logged_in = logged_in, 
                          page = request.url_rule.rule, 
                          stages = stg_list
                        )



@admin_pages.route('/admin/projects', methods=['GET', 'POST'] )
def projects():
  logged_in = is_logged_in() 
  if not logged_in :
    return redirect(url_for('auth.auth'))

  if logged_in != 'admin' :
    return redirect(url_for('index.homepage'))

  stg_list = Stages.select()

  if request.method == 'POST' :
    # get new project name
    params = request.form

    project_name = params.get('project_new_name')
    project_desc = params.get('project_new_description')
    project_git  = params.get('project_new_giturl')

    if len(project_name) <= 2 :
      return render_template( 'admin_projects.html', 
                              __version__ = __version__, 
                              logged_in = logged_in, 
                              page = request.url_rule.rule, 
                              stages = stg_list,
                              msg = "Слишком короткое название для проекта"
                            )

    # try to add new project
    try :
      Projects.create( name = project_name, description = project_desc, git_url = project_git )
      print("""[%s][DEBUG] Try to creat new project [%s]""" % (datetime.now(), project_name ) )
      # log start
      msg = """IP: %s, PROJECT: %s""" % ( request.remote_addr, project_name )
      log_action(session['username'], 'NEW PROJECT', msg)
      # log end 

      projects = Projects.select()
      msg = """Проект [%s] добавлен""" % project_name
      return render_template( 'admin_projects.html', 
                              __version__   = __version__, 
                              logged_in     = logged_in, 
                              page          = request.url_rule.rule, 
                              stages        = stg_list,
                              projects      = projects
                            )
    
    except Exception as e :
      print("""[%s][ERROR] [%s]""" % (datetime.now(), e ) )
      projects = Projects.select().order_by(Projects.name)
      msg = """Не удалось добавить проект [%s]. Возможно он уже существует.""" % project_name
      return render_template( 'admin_projects.html', 
                              __version__   = __version__, 
                              logged_in     = logged_in, 
                              page          = request.url_rule.rule, 
                              stages        = stg_list,
                              projects      = projects
                            )








  projects = Projects.select()
  return render_template( 'admin_projects.html', 
                          __version__   = __version__, 
                          logged_in     = logged_in, 
                          page          = request.url_rule.rule, 
                          stages        = stg_list,
                          projects      = projects
                        )


