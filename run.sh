#!/bin/bash

NUM_WORKERS=1
TIMEOUT=30
PORT=9010

export DUTY_LDAP_SERVER=ldap://ldap.example.int
export DUTY_LDAP_DOMAIN=example.int
export DUTY_LDAP_BASEDN='ou=Users,dc=example,dc=int'
export DUTY_LDAP_GROUPDN='OU=Groups,DC=example,DC=int'

export DUTY_DB_NAME=duty_board
export DUTY_DB_USER=duty_board
export DUTY_DB_PASS=duty_board
export DUTY_DB_PORT=5432
export DUTY_DB_HOST=m362pg-dev

GUNICORN_CMD_ARGS="--bind=0.0.0.0:$PORT --timeout $TIMEOUT --workers=$NUM_WORKERS --log-level=debug --reload" gunicorn main:app

