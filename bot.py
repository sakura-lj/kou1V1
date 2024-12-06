import nonebot
import os
from os import path
import config
import sys
import config

if __name__ == '__main__':
    nonebot.init(config)

    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        bundle_dir = sys._MEIPASS
        plugin_dir = os.path.join(bundle_dir, 'MyPlugin', 'plugins')
    else:
        plugin_dir = path.join(path.dirname(__file__), 'MyPlugin', 'plugins')

    nonebot.load_plugins(
        plugin_dir,
        'MyPlugin.plugins'
    )
    nonebot.run()