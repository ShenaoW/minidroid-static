
import os
import sys
import json
import minium
import config as config
from loguru import logger 
from utils.utils import get_wxapkg_paths, get_miniapp_paths
from utils.wxapkg_decoder import decompile_wxapp
from strategy.violation_checker import ViolationChecker
from miniapp import MiniApp

# import faulthandler
# sys.path.append('..')
# faulthandler.enable()

def handle_wxapkgs(wxapkgs_dir='dataset/wxapkgs', save_json=False):
    '''
        Decode wxapkgs in the directory.

        -------
        Parameters:
        - wxapkgs_dir: str
            default 'dataset/wxapkgs'
        - save_json: bool/str
            default False, you can specify the path to save decode json result.

        -------
        Return: None
    '''
    wxapkg_paths = get_wxapkg_paths(wxapkgs_dir)
    decompile_pkg = []
    for wxapkg_path in wxapkg_paths:
        if decompile_wxapp(wxapkg_path):
            decompile_pkg.append(wxapkg_path.replace('.wxapkg', '').replace('wxapkgs', 'miniprograms'))
    if save_json:
        res = json.dumps(decompile_pkg, indent=2)
        with open(save_json, 'w') as fp:
                fp.write(res)

def mini_droid():
    project_path = "H:\[粉粉小红花]\Mobile Security\Miniapp\Open Source Code\MiniApp src\录音器"
    mini = minium.Minium({
        "project_path": project_path,
        "dev_tool_path": "D:\微信web开发者工具\cli.bat",
    })
    print(mini.get_system_info())


def check_compliance_violations():
    logger.add('dataset/output.log')
    with open('dataset/dataset.json', 'r') as f:
        miniapp_paths = json.load(f)
    for miniapp_path in miniapp_paths:
        logger.info('[Start] Static analysis of {}'.format(miniapp_path))
        try:
            miniapp = MiniApp(miniapp_path=miniapp_path)
            checker = ViolationChecker(miniapp=miniapp)
            if checker.blanket_reqs != None or checker.req_before_use != None \
                    or checker.compulsory_reqs != None:
                violations = {
                    'req_before_use': checker.req_before_use,
                    'blanket_reqs': checker.blanket_reqs,
                    'compulsory_req': checker.compulsory_reqs
                }
                with open(miniapp.miniapp_path.replace('miniprograms', 'comp_vios')+'.json', 'w') as fp:
                    json.dump(violations, fp, indent=4)
                logger.critical('[ViolationsFound] Compliance violations found at {}'.format(miniapp_path))
            logger.info('[Finish] Static Analysis finished')
        except Exception as e:
            logger.error(e)
        

if __name__ == '__main__':
    check_compliance_violations()

    # FIXED: 'Page' object has no attribute 'pdg_node'
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx4c912d1abd56b887')   __plugin__
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wxa4653b2a6f953b53')   __plugin__
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx45d379cfc179c2db')   __plugin__

    # FIXED: KeyError 'name'
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx70c645ccf95a39e1')
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx8bfc50da8019a4dc')
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wxa0598a26b6a71cd3')

    # FIXED: unhashable type: 'list' in call_expr_value == 'wx.authorize'?
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx91beb99727a5936f')
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx9588480be4a6d9db')
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx9e6e9ee3c2ec7751')


    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wxaffdef2d93ac0cf5')
    # checker = ViolationChecker(miniapp=miniapp)
    # if checker.blanket_reqs != None or checker.req_before_use != None \
    #                 or checker.compulsory_reqs != None:
    #             violations = {
    #                 'req_before_use': checker.req_before_use,
    #                 'blanket_reqs': checker.blanket_reqs,
    #                 'compulsory_req': checker.compulsory_reqs
    #             }
    #             with open(miniapp.miniapp_path.replace('miniprograms', 'comp_vios'), 'w') as fp:
    #                 json.dump(violations, fp, indent=4)
    # print('success')