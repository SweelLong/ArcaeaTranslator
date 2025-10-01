# ArcaeaTranslator

- Python 脚本旨在将 Arcaea 的 *.mo 二进制语言文件转换成可编辑的 *.po 文件
- 通过匹配 tl 文件夹下的 zh-Hans.po 与父目录下该文件的差异以提取新增的翻译条目
- 以父目录下的语言文件为基准，快速机翻生成其他语言的翻译
- 同时内置了 mo 与 po 文件的相互转换功能
- [百度翻译API](https://fanyi-api.baidu.com/manage/developer)

- 使用方法很简单：
- 
    1.配置完成 API 基本信息

    2.在 tl 文件夹放置没有使用过的语言文件，如需 en 翻译请自行破解硬编码

    3.在父目录下留一份 zh-Hans.mo 或者 zh-Hans.po 文件作为模板

    4.模板文件会以po文件为主，请在父目录下的模板po文件中编辑文本，不存  在po则会自动解析mo文件

    5.运行 main.py 脚本，将会自动生成其他语言的翻译并输出到 tl_output 文件夹

Copyright © 2025 SweelLong