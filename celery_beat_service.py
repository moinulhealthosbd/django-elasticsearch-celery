'''
Run celery as a Windows service
Usage:
python celery_service.py install
python celery_service.py start
python celery_service.py stop
python celery_service.py remove
'''
import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import subprocess
import sys
import os
from pathlib import Path
import logging
import time

# Default: the directory of this script
INSTDIR = Path(__file__).parent

# The virtual environment name
VIRTUALENV_NAME = 'venv'

# The path of python Scripts
# Usually it is in path_to/venv/Scripts.
# If it is already in system PATH, then it can be set as ''
PYTHONSCRIPTPATH = INSTDIR / VIRTUALENV_NAME / '/Scripts'

# The directory name of django project
# Note: it is the directory at the same level of manage.py
# not the parent directory
PROJECTDIR = 'config'


# Log files for worker and beat
WROKER_LOG_FILE_NAME = "celery_worker.log"
BEAT_LOG_FILE_NAME = "celery_beat.log"
CELERY_BASIC_LOG_FILE = 'celery_service.log'

logging.basicConfig(
    filename = INSTDIR / CELERY_BASIC_LOG_FILE,
    level = logging.DEBUG, 
    format = '[%(asctime)-15s: %(levelname)-7.7s] %(message)s'
)

class CeleryService(win32serviceutil.ServiceFramework):

    _svc_name_ = "Celery"
    _svc_display_name_ = "Celery Distributed Task Queue Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        logging.info('Stopping {name} service ...'.format(name=self._svc_name_))
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        sys.exit()

    def SvcDoRun(self):
        logging.info('Starting {name} service ...'.format(name=self._svc_name_))
        # Change directory so that proj worker can be found
        os.chdir(INSTDIR)
        logging.info('cwd: ' + os.getcwd())
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        worker_command = '"{celery_path}" -A {proj_dir} worker -f "{log_path}" --loglevel=info --pool=solo'.format(
            celery_path=PYTHONSCRIPTPATH / 'celery.exe',
            proj_dir=PROJECTDIR,
            log_path=INSTDIR / WROKER_LOG_FILE_NAME)
        
        beat_command = '"{celery_path}" -A {proj_dir} beat -f "{log_path}" -l INFO'.format(
            celery_path=PYTHONSCRIPTPATH / 'celery.exe',
            proj_dir=PROJECTDIR,
            log_path=INSTDIR / BEAT_LOG_FILE_NAME)
        
        logging.info('beat-command: ' + beat_command)
        logging.info('worker-command: ' + worker_command)

        proc = subprocess.run(beat_command + '&&' + worker_command, capture_output=True, shell=True)
        logging.info('pid: {pid}'.format(pid=proc.pid))
        self.timeout = 30
        
        while True:
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                # stop signal encountered
                # terminate process 'proc'
                PROCESS_TERMINATE = 1
                handle = win32api.OpenProcess(PROCESS_TERMINATE, False, proc.pid)
                win32api.TerminateProcess(handle, -1)
                win32api.CloseHandle(handle)           
                break
            

if __name__ == '__main__':
   win32serviceutil.HandleCommandLine(CeleryService)