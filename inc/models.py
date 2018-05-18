# -*- coding: UTF-8 -*-
from datetime       import datetime
from peewee         import *
from os             import environ
from playhouse.pool import PooledPostgresqlExtDatabase

import sys

# read db credentials from environment
DB_NAME = environ.get('DUTY_DB_NAME', 'touchbank_duty')
DB_USER = environ.get('DUTY_DB_USER', 'touchbank')
DB_HOST = environ.get('DUTY_DB_HOST', 'localhost')
DB_PORT = environ.get('DUTY_DB_PORT', 5432)
DB_PASS = environ.get('DUTY_DB_PASS', 'password')

#pg_sql = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, autocommit=True, autorollback=True)    
pg_sql = PooledPostgresqlExtDatabase(   database=DB_NAME,
                                        user=DB_USER,
                                        password=DB_PASS,
                                        host=DB_HOST,
                                        port=DB_PORT,
                                        max_connections=8,
                                        stale_timeout=300, # 300 sec = 5 min
                                        autocommit=True,
                                        autorollback=True, )
pg_sql.close()


class BaseModel(Model):
  class Meta:
    database = pg_sql

# Пользователи
class Users(BaseModel):
  name        = CharField(unique=True)
  admin       = BooleanField(default=False)
  timestamp   = TimestampField(default=int( datetime.timestamp(datetime.now()) ))
  sid         = CharField(unique=True)
  token       = CharField(null=True)

# среды для деплоя
class Stages(BaseModel):
  name        = CharField(unique=True)

# права доступа для пользователя
class Access(BaseModel):
  user        = ForeignKeyField(Users)
  stage       = ForeignKeyField(Stages)
  access      = BooleanField(default=True)

# список проектов для прикрепления
class Projects(BaseModel):
  name        = CharField(unique=True)
  description = TextField(null=True)
  git_url     = CharField(null=True)
  active      = BooleanField(default=True)

# параметры для проектов
class Params(BaseModel):
  project     = ForeignKeyField(Projects)
  stage       = ForeignKeyField(Stages)
  type        = CharField() # variable, tag, token, ref, project_id
  name        = CharField(null=True) # название параметра
  value       = CharField(null=True) # value for type
  ask_user    = BooleanField(default=True) # if ask_user == True -> show input box
  description = CharField(null=True) # Description for this param, if needed

# запущенные задачи
class Jobs(BaseModel):
  author      = CharField(null=True)
  project     = ForeignKeyField(Projects)
  stage       = ForeignKeyField(Stages)
  timestamp   = TimestampField(default=int( datetime.timestamp(datetime.now()) ))
  job_url     = CharField(null=True)

class Logs(BaseModel):
  author      = CharField() # 
  action      = CharField() #
  message     = TextField() # Old value, new value
  timestamp   = TimestampField(default=int( datetime.timestamp(datetime.now()) ))

# матрица доступа к проектам. По-умолчанию доступа нет никуда, админ добавляет.
class Matrix(BaseModel):
  user        = ForeignKeyField(Users)
  stage       = ForeignKeyField(Stages)
  project     = ForeignKeyField(Projects)
  access      = BooleanField(default=False)


def init_db():
  # connect to DB
  pg_sql.connect()
  pg_sql.create_tables( [Users, Stages, Access, Projects, Params, Jobs, Logs, Matrix] )
  pg_sql.close()
 
