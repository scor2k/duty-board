## Duty Board

### Desctiption
* GUI для запуска Ansible-задач, расположенных в GitLab с помощью GitLab-CI
* PostgreSQL в качестве СУБД.
* Любое количество сред запуска (DEV, TST, ...)
* Доменная авторизация и матричное разграничение прав доступа (пользователь - проект - среда запуска)
* Настройка параметров запуска проекта через раздел администрирование
* Логирование всех изменений параметров
* Логирование всех запусков задач

### Changelog

*0.3.0*
* first github version

*0.2.14*
* preparing for github

*0.2.13*
* Fixed bug when try to change page in tasks section (open logs)

*0.2.12*
* When configure project you can use list of params divided ';'
* Add hints when configure project
* Add custom color for ALL stage (secondary)

*0.2.11*
* Bugfix bug with access rights.

*0.2.10*
* Change 0 in `allow_list` to -1
* Add logging for `project_ids` and `allow_list`

*0.2.9*
* Hide global params from regular users (except variables)
* Hide curl from regular users

*0.2.8*
* Change ERROR to DEBUG when get Exception in before_request & after_request
* Fixed bug with undefined message in route/exec.py
* Extend debuggin in utils.py for post/get requests
* Remove all spaces in the end and start

*0.2.7*
* Add PostgreSQL connection pool
* Add before and after triggers for connect and close db connections

*0.2.6*
* Info logging level
* docker-compose with graylog 

*0.2.5*
* Debug logging

*0.2.4* - 2018/04/13
* Bugfix users's rights and admin rights

*0.2.3* - 2018/04/13
* User's rights add and remove

*0.2.2* - 2018/04/12
* Show all jobs-task but active only one included stage name
* add ALL stage for global tasks
* Remove params allow with logging

*0.2.1*
* Bufix rollback error
* Add simple admin page for users

*0.2.0* 
* Initial Release installed on infra
