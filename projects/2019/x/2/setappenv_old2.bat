set FLASK_APP=application.py
set FLASK_ENV=development

set _COMMAND_TO_PROCESS=python -c "import secrets; print(secrets.token_bytes())"
set _COMMAND_TO_EXECUTE=set SECRET_KEY=%%G
for /f %%G in ('%_COMMAND_TO_PROCESS%') do %_COMMAND_TO_EXECUTE%
set _COMMAND_TO_PROCESS=
set _COMMAND_TO_EXECUTE=

