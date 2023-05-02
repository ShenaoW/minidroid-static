import json
import pprint
import config as config
from miniapp import MiniApp, Page
from mdg import UTG, FCG
from pathlib import Path


class ConsistencyAnalyzer():
    def __init__(self, miniapp: MiniApp, privacy_policy: Path):
        self.miniapp = miniapp
        self.reachable_sensi_apis = set()
        self.unreachable_sensi_apis = set()
        self.set_reachable_sensi_apis()
        with open(str(privacy_policy), 'r', encoding='utf-8') as fp:
            self.privacy_policy = json.load(fp=fp)

    def set_reachable_sensi_apis(self):
        reachable_page = self.get_reachable_page()
        sensi_apis = self.miniapp.sensi_apis
        for sensi_page in sensi_apis.keys():
            if sensi_page in reachable_page:
                reachable_func = self.get_reachable_func(self.miniapp.pages[sensi_page])
                for sensi_api in sensi_apis[sensi_page].keys():
                    for func in sensi_apis[sensi_page][sensi_api]:
                        if sensi_apis[sensi_page][sensi_api] in reachable_func:
                            self.reachable_sensi_apis.add(sensi_api)
                    else:
                        self.unreachable_sensi_apis.add(sensi_api)
            else:
                for sensi_api in sensi_apis[sensi_page].keys():
                    self.unreachable_sensi_apis.add(sensi_api)
    
    def get_reachable_page(self):
        utg = UTG(self.miniapp)
        utg_dict = utg.get_utg_dict()
        if len(utg_dict):
            reachable = self.dfs(utg_dict, key='MiniApp', reachable=set())
        else:
            reachable=set()
        return reachable
    
    def get_reachable_func(self, page: Page):
        fcg = FCG(page)
        fcg_dict = fcg.get_fcg_dict()
        if len(fcg_dict):
            reachable = self.dfs(fcg_dict, key=page.page_path, reachable=set())
        else:
            reachable = set()
        return reachable

    def dfs(self, utg_dict, key, reachable: set):
        for value in utg_dict[key]:
            reachable.add(value)
            if value in utg_dict.keys():
                self.dfs(utg_dict, key=value, reachable=reachable)
        return reachable
    
    def reachable_sensi_apis_to_scopes(self):
        reachable_scopes = set()
        for sensi_api in self.reachable_sensi_apis:
            reachable_scopes.add(config.SENSITIVE_API[sensi_api])
        return reachable_scopes
    
    def privacy_policy_to_scopes(self):
        pp_scopes = set()
        for desc in self.privacy_policy['privacy_detail_list']['item']:
            if '开发者将在获取你的明示同意后' in desc:
                scope = desc.split('，')[-1]
                pp_scopes.add(scope)
            elif '用于' in desc:
                scope = desc.split('，')[0].replace('开发者', '')
                pp_scopes.add(scope)
        return pp_scopes

    def consistency_analysis(self):
        pp_scopes = self.privacy_policy_to_scopes()
        if len(pp_scopes):
            reachable_scopes = self.reachable_sensi_apis_to_scopes()
            redundant_scopes = list(set(pp_scopes) - set(reachable_scopes))
            missing_scopes = list(set(reachable_scopes) - set(pp_scopes))
            return redundant_scopes, missing_scopes
        else:
            return None, None

if __name__ == '__main__':
    miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx81e4613b8a60e2ea')
    analyzer = ConsistencyAnalyzer(miniapp=miniapp, privacy_policy=Path('/root/minidroid/dataset/privacy_policy/wx81e4613b8a60e2ea.json'))
    pprint.pprint(analyzer.consistency_analysis())

    # pprint.pprint(analyzer.sensi_apis)
    
    # test get_reachable_page
    # pprint.pprint(analyzer.get_reachable_page())

    # test get_reachable_func
    # for page in miniapp.pages.values():
    #     pprint.pprint(analyzer.get_reachable_func(page))
    #     break
