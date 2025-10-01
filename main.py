"""
ArcaeaTranslator
Python 脚本旨在将 Arcaea 的 *.mo 二进制语言文件转换成可编辑的 *.po 文件
通过匹配 tl 文件夹下的 zh-Hans.po 与父目录下该文件的差异以提取新增的翻译条目
以父目录下的语言文件为基准，快速机翻生成其他语言的翻译
同时内置了 mo 与 po 文件的相互转换功能
百度翻译API：https://fanyi-api.baidu.com/manage/developer
使用方法很简单：
1.配置完成 API 基本信息
2.在 tl 文件夹放置没有使用过的语言文件，如需 en 翻译请自行破解硬编码
3.在父目录下留一份 zh-Hans.mo 或者 zh-Hans.po 文件作为模板
4.模板文件会以po文件为主，请在父目录下的模板po文件中编辑文本，不存在po则会自动解析mo文件
5.运行 main.py 脚本，将会自动生成其他语言的翻译并输出到 tl_output 文件夹
Copyright (c) 2025 SweelLong
"""
import hashlib
import os
import polib
import random
import requests
import subprocess

def mo_to_po(mo_file_path, po_file_path):
    try:
        subprocess.run([r'gettext\msgunfmt', mo_file_path, '-o', po_file_path], check=True, capture_output=True, text=True)
    except Exception as e:
        print(f"解析失败: {str(e)}")
    else:
        print(f"解析成功: {mo_file_path} -> {po_file_path}")

def parse_po_file(po_file_path) -> dict:
    with open(po_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        msg = {}
        msgid = ""
        msgstr = ""
        type = -1
        for line in lines:
            if line.startswith("msgid "):
                if type != -1:
                    msg.setdefault(msgid, msgstr)
                    msgid = ""
                    msgstr = ""
                type = 0
                line = line.strip()[6:]
                msgid += str(eval(line))
            elif line.startswith("msgstr "):
                type = 1
                line = line.strip()[7:]
                msgstr += str(eval(line))
            elif type == 0 and line.startswith('"'):
                msgid += str(eval(line))
            elif type == 1 and line.startswith('"'):
                msgstr += str(eval(line))
        msg.setdefault(msgid, msgstr)
        return msg

def get_language_code_from_filepath(path) -> str:
    filename = os.path.basename(path)
    lang_code = filename.split('.')[0]
    return lang_code

def get_translated_text(text, origin_lang, target_lang) -> str:
    appid = '问号'
    appkey = '问号'
    lang_code_to_baidu = {
        'en': 'en',
        'ja': 'jp',
        'ko': 'kor',
        'zh-Hans': 'zh',
        'zh-Hant': 'cht'
    }
    from_lang = lang_code_to_baidu[origin_lang]
    to_lang =  lang_code_to_baidu[target_lang]
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path
    salt = random.randint(32768, 65536)
    sign = hashlib.md5((appid + text + str(salt) + appkey).encode('utf-8')).hexdigest()
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': text, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    result = requests.post(url, params=payload, headers=headers).json()
    for item in result['trans_result']:
        text = text.replace(item['src'], item['dst'])
    return text

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    template_mo = "zh-Hans.mo"
    template_po = "zh-Hans.po"
    generate_en_po = True
    if not os.path.exists(template_po):
        if not os.path.exists(template_mo):
            print(f"模板文件不存在: {template_mo}")
            exit(1)
        mo_to_po(template_mo, template_po)
    mo_dir = "tl"
    if not os.path.exists(mo_dir):
        os.makedirs(mo_dir)
    output_dir = "tl_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    po_files = []
    for mo_file in os.listdir(mo_dir):
        if not mo_file.endswith('.mo'):
            continue
        mo_file_path = os.path.join(mo_dir, mo_file)
        po_file_path = os.path.join(mo_dir, mo_file.replace('.mo', '.po'))
        mo_to_po(mo_file_path, po_file_path)
        po_files.append(po_file_path)
    print("=" * 50)
    template_dict = parse_po_file(template_po)
    print(f"模板文件 {template_po} 加载完毕: 共 {len(template_dict)} 条翻译")
    tl_origin_dict = parse_po_file(f"{mo_dir}/{template_po}")
    print(f"原始文件 {mo_dir}/{template_po} 加载完毕: 共 {len(tl_origin_dict)} 条翻译")
    if generate_en_po:
        en_po_path = os.path.join(mo_dir, 'en.po')
        if not os.path.exists(en_po_path):
            with open(en_po_path, 'w', encoding='utf-8') as f:
                for key, _ in template_dict.items():
                    f.write(f'msgid "{key.replace("\n", "\\n").replace("\"", "\\\"")}"\n')
                    f.write(f'msgstr "{key.replace("\n", "\\n").replace("\"", "\\\"")}"\n')
                    f.write('\n')
                print(f"已自动生成 {en_po_path} 追加英文翻译！ - 具体需要硬编码修改才能使用哦！")

            generate_en_po = False
            po_files.append(en_po_path)
    unique_dict = {}
    for key, value in template_dict.items():
        if key and tl_origin_dict.get(key) != value:
            unique_dict[key] = value
            print(f"翻译条目: 对 {key} 键有 {tl_origin_dict.get(key)} -> {value}")
    print(f"新增翻译: 共 {len(unique_dict)} 条")
    template_lang_code = get_language_code_from_filepath(template_po)
    for po_file in po_files:
        this_lang_code = get_language_code_from_filepath(po_file)
        this_po_dict = parse_po_file(po_file)
        print(f"正在处理 {po_file} 语言代码: {this_lang_code}")
        if template_lang_code == this_lang_code:
            for key, value in unique_dict.items():
                this_po_dict.update({key:value})
        else:
            for key, value in unique_dict.items():
                this_po_dict.update({key:get_translated_text(value, template_lang_code, this_lang_code)})
        with open(po_file, 'w', encoding='utf-8') as f:
            for key, value in this_po_dict.items():
                f.write(f'msgid "{key.replace("\n", "\\n").replace("\"", "\\\"")}"\n')
                f.write(f'msgstr "{value.replace("\n", "\\n").replace("\"", "\\\"")}"\n')
                f.write('\n')
            print(f"已成功更新 {po_file} 翻译！")
        mo_file = os.path.join(output_dir, this_lang_code + '.mo')
        try:
            po = polib.pofile(po_file)
            po.save_as_mofile(mo_file)
        except Exception as e:
            print(f"编译失败: {str(e)}")
            continue
        print(f"编译成功: {po_file} -> {mo_file}")
print("=" * 50)
print("处理完毕，已保存到 tl_output 文件夹！")