import json

appids_1w = set()
appids_11w = set()

with open("/root/minidroid/dataset/dataset.json", 'r') as fp:
    miniprograms = json.load(fp)

for miniprogram in miniprograms:
    appids_1w.add(miniprogram.split("/")[-1])

with open("/root/minidroid/dataset/miniprograms-11w.json", "r") as fp:
    miniprograms = json.load(fp)

for miniprogram in miniprograms:
    appids_11w.add(miniprogram.split("/")[-1][:-3])

print(len(appids_1w))
print(len(appids_11w))

print(len(appids_1w & appids_11w))
print(appids_1w & appids_11w)
print(len(appids_1w | appids_11w))