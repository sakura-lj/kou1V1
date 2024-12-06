from PyInstaller.__main__ import run

if __name__ == '__main__':
    opts = [
            '--paths', 'D:\\Python\\Python39\\Lib\\site-packages\\nonebot2\\adapters\\cqhttp',
            '--python', 'D:\\Python\\Python39\\python.exe',
            '--onefile',
            '--windowed',
            '--add-data', 'config.py;.',
            '--add-data', 'MyPlugin/plugins;MyPlugin/plugins',
            'bot.py'
            # 以上为构建bot.exe
            # '--windowed',
            # '--name', '扣1神器v1.1.0',
            # '--add-data', 'bot.exe;.',
            # '--add-binary','bot.exe;.',
            # 'main.py'
            ]
#先构建bot.exe，再构建扣1神器
    run(opts)