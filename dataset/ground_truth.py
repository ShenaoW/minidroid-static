import json
import shutil

with open("/root/minidroid/dataset/ground_truth_v2.json", 'r') as fp:
    data = json.load(fp)

for miniapp in data:
    source_folder = '/root/minidroid/result/sensi_apis_trigger_path/{}.json'.format(miniapp)
    target_folder = '/root/minidroid/dataset/groundtruth_v2/sensi_apis/'

    shutil.copy2(source_folder, target_folder)
    print("[Success] {}".format(miniapp))
