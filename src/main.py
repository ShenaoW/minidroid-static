import json
from loguru import logger
from bs4 import BeautifulSoup
from utils.utils import get_wxapkg_paths
from utils.wxapkg_decoder import decompile_wxapkg_with_unveilr
from strategy.violation_checker import ViolationChecker
from miniapp import MiniApp


def handle_wxapkgs(wxapkgs_dir='dataset/wxapkgs', save_json=None):
    """
        Decode wxapkgs in the directory.

        -------
        Parameters:
        - wxapkgs_dir: str
            default 'dataset/wxapkgs'
        - save_json: bool/str
            default False, you can specify the path to save decode json result.

        -------
        Return: None
    """
    logger.add('src/log/dec_wxapkgs.log')
    wxapkg_paths = get_wxapkg_paths(wxapkgs_dir)
    decompile_pkg = []
    for wxapkg_path in wxapkg_paths:
        if decompile_wxapkg_with_unveilr(wxapkg_path, output_path='dataset/miniprograms-11w/'+wxapkg_path.split('/')[-1].replace('.wxapkg', '')):
            decompile_pkg.append(wxapkg_path.replace('.wxapkg', '').replace('wxapkgs', 'miniprograms'))
    if save_json is not None:
        res = json.dumps(decompile_pkg, indent=2)
        with open(save_json, 'w', encoding='utf-8') as fp:
            fp.write(res)

def check_compliance_violations():
    logger.add('src/log/comp_vios.log')
    with open('dataset/dataset.json', 'r', encoding='utf-8') as fp:
        miniapp_paths = json.load(fp)
    for miniapp_path in miniapp_paths:
        logger.info('[Start] Static analysis of {}'.format(miniapp_path))
        try:
            miniapp = MiniApp(miniapp_path=miniapp_path)
            checker = ViolationChecker(miniapp=miniapp)
            if checker.blanket_reqs is not None or checker.req_before_use is not None \
                    or checker.compulsory_reqs is not None:
                violations = {
                    'req_before_use': checker.req_before_use,
                    'blanket_reqs': checker.blanket_reqs,
                    'compulsory_req': checker.compulsory_reqs
                }
                with open(miniapp.miniapp_path.replace('miniprograms', 'comp_vios') + '.json', 'w') as fp:
                    json.dump(violations, fp, indent=4)
                logger.critical('[ViolationsFound] Compliance violations found at {}'.format(miniapp_path))
            logger.info('[Finish] Static Analysis finished')
        except Exception as e:
            logger.error(e)

def check_sensi_apis():
    sensi_apis_json = {}
    logger.add('src/log/sensi_apis.log')
    with open('dataset/dataset.json', 'r', encoding='utf-8') as fp:
        miniapp_paths = json.load(fp)
    for miniapp_path in miniapp_paths:
        logger.info('[Start] Static analysis of {}'.format(miniapp_path))
        try:
            miniapp = MiniApp(miniapp_path=miniapp_path)
            sensi_apis_json[miniapp_path] = miniapp.sensi_apis
            with open(miniapp.miniapp_path.replace('miniprograms', 'sensi_apis') + '.json', 'w') as fp:
                json.dump(miniapp.sensi_apis, fp, indent=4)
            logger.info('[Finish] Static Analysis finished')
        except Exception as e:
            logger.error(e)
    with open('dataset/sensi_apis.json', 'w') as fp:
        json.dump(sensi_apis_json, fp, indent=4)

def get_sensi_page_text():
    result_json = {}
    with open('dataset/sensi_apis_result.json', 'r', encoding='utf-8') as fp:
        json_data = json.load(fp)
    for miniapp_key in json_data.keys():
        sensi_api_dict = {}
        for sensi_api in json_data[miniapp_key].keys():
            page_dict = {}
            for page in json_data[miniapp_key][sensi_api]:
                soup = BeautifulSoup(open(page + '.wxml'), 'html.parser')
                page_dict[page] = soup.text
            sensi_api_dict[sensi_api] = page_dict
        result_json[miniapp_key] = sensi_api_dict
    with open('./dataset/sensi_page_text.json', 'w') as fp:
        json.dump(result_json, fp, indent=4)

def draw_utg():
    logger.add('src/log/utg.log')
    with open('dataset/dataset.json', 'r', encoding='utf-8') as fp:
        miniapp_paths = json.load(fp)
    for miniapp_path in miniapp_paths:
        logger.info('[Start] Static analysis of {}'.format(miniapp_path))
        try:
            miniapp = MiniApp(miniapp_path=miniapp_path)
            miniapp.draw_utg()
        except Exception as e:
            logger.error(e)

def draw_fcg():
    logger.add('src/log/fcg.log')
    with open('dataset/dataset.json', 'r', encoding='utf-8') as fp:
        miniapp_paths = json.load(fp)
    for miniapp_path in miniapp_paths:
        logger.info('[Start] Static analysis of {}'.format(miniapp_path))
        try:
            miniapp = MiniApp(miniapp_path=miniapp_path)
            for page in miniapp.pages.values():
                page.draw_fcg()
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    handle_wxapkgs('dataset/wxapkgs-11w', save_json='dataset/dataset11w-dec.json')
    # check_compliance_violations()
    # check_sensi_apis()
    # get_sensi_page_text()
    # draw_utg()
    # draw_fcg()

    # test check_sensi_apis
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx9c7a3b1a32b7116c')
    # with open(miniapp.miniapp_path.replace('miniprograms', 'sensi_apis')+'.json', 'w') as fp:
    #     json.dump(miniapp.sensi_apis, fp, indent=4)
    # print('success')

    # Test check_compliance_violations
    # miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx4efaefee87cecc64')
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
