import subprocess
from pathlib import Path

from loguru import logger


def decompile_wx_miniapp(package_path):
    """
    Decompile wx miniapp
    @param package_path: Path to package.
    @return:
    """
    decompiler_tool = Path(__file__) / "unveilr@2.0.1.exe"
    cmdline = [decompiler_tool, package_path]
    outputs = subprocess.check_output(cmdline)
    for i in outputs:
        if b"INFO" in i:
            logger.info(i.decode())
        elif b"WARN" in i:
            logger.warning(i.decode())
        elif b"ERROR" in i:
            logger.error(i.decode())
            return False
    return True
