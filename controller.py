import subprocess

from main import logger


def execute_cmd_on_controller(cmd, timeout=10):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, error = p.communicate()
    res = output.decode()
    if p.wait(timeout=timeout) != 0:
        logger.error("execute cmd %s on controller failed after time %s"%(cmd, timeout))
        raise Exception("execute cmd %s on controller failed after time %s"%(cmd, timeout))
    else:
        logger.info("execute cmd %s on controller success"%cmd)
        logger.info("result: %s"% res)