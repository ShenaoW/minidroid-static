import os
import utils.utils as utils
from utils.wxapkg_decoder import decompile_wxapkg_with_wxUnpacker

wxapkgs_dir = "dataset/WeMint-TP/wxapkgs"
output_dir = "/root/minidroid/dataset/WeMint-TP/miniprograms"
for miniapp in os.listdir(wxapkgs_dir):
    decompile_wxapkg_with_wxUnpacker(os.path.join(wxapkgs_dir, miniapp))