# -*- coding: UTF-8 -*-
from os       import environ

__version__ = "0.3.0"

# Tokens
GITLAB_TOKEN    = environ.get('DUTY_GITLAB_TOKEN', '')
GITLAB_URL      = environ.get('DUTY_GITLAB_URL', 'https://git-dev.example.ru/api/v4/projects')
