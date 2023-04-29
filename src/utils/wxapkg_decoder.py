import subprocess
import platform
from pathlib import Path
from loguru import logger


class UnsupportedOSException(Exception):
    pass

def decompile_wxapkg(wxapkg, output_path=None):
    """
    Decompile wx miniapp
    @param package_path: Path to package.
    @return:
    """
    system = platform.system()
    machine = platform.machine()

    if system == 'Linux':
        if machine.startswith('arm'):
            # Linux ARM 架构
            decompiler_tool = Path(__file__).parent / "unveilr/unveilr@2.0.1-linux-arm64"
        else:
            # Linux x86 架构
            decompiler_tool = Path(__file__).parent / "unveilr/unveilr@2.0.1-linux-x64"
    elif system == 'Windows':
        # 执行 Windows x86 架构
        decompiler_tool = Path(__file__).parent / "unveilr/unveilr@2.0.1-win-x64.exe"
    elif system == 'Darwin':
        if machine.startswith('arm'):
            # macOS ARM 架构
            decompiler_tool = Path(__file__).parent / "unveilr/unveilr@2.0.1-macos-arm64"
        else:
            # macOS x86 架构
            decompiler_tool = Path(__file__).parent / "unveilr/unveilr@2.0.1-macos-x64"
    else:
        # 不支持的操作系统类型
        logger.error(("Unsupported OS: {} {}".format(system, machine)))
        raise UnsupportedOSException("Unsupported OS: {} {}".format(system, machine))
    
    if output_path is not None:
        cmdline = [decompiler_tool, wxapkg, '-o', output_path, '-f']
    else:
        cmdline = [decompiler_tool, wxapkg, '-f']

    try:
        subprocess.check_output(cmdline)
        logger.info('Decompile Success: {}'.format(wxapkg))
        return True
    except Exception as e:
        logger.error(e)
        return False

if __name__ == '__main__':
    wxapkg_path = '/root/unveilr/wxapkgs/wx0012c9069fddb0d3-pc.wxapkg'
    decompile_wxapkg(wxapkg_path, output_path='dataset/miniprograms-11w/'+wxapkg_path.split('/')[-1])