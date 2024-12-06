# 1. kou1V1简介

检测QQ群里出现关键词”**扣一**“，就自动发送消息"**1**"，该版本是V1.0版本。

实现路线为QQNT+[LiteLoaderQQNT](https://github.com/LiteLoaderQQNT/LiteLoaderQQNT?tab=readme-ov-file)+[nonebot1](https://github.com/nonebot/nonebot)

# 2. 使用方法

（1）安装好环境，建议用一键安装工具：[install_llob](https://github.com/super1207/install_llob)

（2）clone代码，然后运行main.c，即可实现

# 3.注意事项

* 我使用的是python3.10，不过这个应该没影响

* 该项目目前2.0正在开发中，其实就是将[nonebot1](https://github.com/nonebot/nonebot)升级为使用[nonebot2](https://github.com/nonebot/nonebot2)框架。经过实测运行速度快了一些（ps:扣一更快了），但是内存开销也大了一些。

***

* 项目中的build.py就是将pyinstaller命令行打包方式，改为运行文件，直接运行build.py就可以获得一个.exe的可运行文件,文件注释中有，因为我的路径管理写的依托答辩，所以得先打包bot.py,然后将得到的bot.exe，作为数据加入到main.c的打包中，最后得出的文件运行才不会报路径错误。


# 4. 致谢

* [install_llob](https://github.com/super1207/install_llob)

* [nonebot](https://github.com/nonebot/nonebot)

* [LLOneBot](https://github.com/LLOneBot/LLOneBot)

* [LiteLoaderQQNT](https://github.com/LiteLoaderQQNT/LiteLoaderQQNT)

