import os
import json
import pprint
import loguru
from miniapp import MiniApp

ground_truth_dir = "/root/minidroid/dataset/groundtruth_v2/miniprograms"
loguru.logger.add("/root/minidroid/dataset/groundtruth_v2/count_api.log")

for miniapp in os.listdir(ground_truth_dir):
    try:
        sensi_apis = {}
        app = MiniApp(os.path.join(ground_truth_dir, miniapp))
        # pprint.pprint(app.sensi_apis)
        for page in app.sensi_apis.keys():
            for api in app.sensi_apis[page]:
                if api not in sensi_apis.keys():
                    sensi_apis[api] = []
                    sensi_apis[api].append(page)
                else:
                    sensi_apis[api].append(page)
        with open("/root/minidroid/dataset/groundtruth_v2/count_api/{}.json".format(miniapp), 'w+') as fp:
            json.dump(sensi_apis, fp, indent=4)
        loguru.logger.info("[Success] {}".format(miniapp))
    except Exception as e:
        loguru.logger.error("[Error] {} {}".format(miniapp, e))
    