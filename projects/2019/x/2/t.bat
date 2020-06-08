set _COMMAND_TO_PROCESS=python -c "import os; print(os.urandom(16))"
set _COMMAND_TO_EXECUTE=set SECRET_KEY=%%G
for /f %%G in ('%_COMMAND_TO_PROCESS%') do %_COMMAND_TO_EXECUTE%
set _COMMAND_TO_PROCESS=
set _COMMAND_TO_EXECUTE=
