# -*- coding: utf-8 -*-
"""根据 docs/面试知识库/ 的目录结构自动生成 zensical.toml 里的 nav 配置。

规则：
- 每个子目录（专题）成为「面试知识库」下的一个分组；
- 专题内的 .md 文件（按文件名排序）成为文章，README.md 固定为「总览」排在末尾；
- 专题标题：去掉目录名末尾的「面试知识讲解」后缀，其余保持原名。

用法：python gen_zensical_config.py
"""
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE, 'docs', '面试知识库')
CONFIG = os.path.join(BASE, 'zensical.toml')
SUFFIX = '面试知识讲解'


def q(s):
    """转成 TOML 双引号字符串。"""
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def read_h1(path):
    """读取 markdown 的第一个一级标题，没有则返回 None。"""
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()
                if line and not line.startswith('#'):
                    return None
    except OSError:
        pass
    return None


def file_title(name):
    name = name[:-3] if name.endswith('.md') else name
    name = re.sub(r'^\d+[_.]', '', name)
    return name.replace('_', ' ').strip() or name


def section_title(folder):
    return folder[: -len(SUFFIX)] if folder.endswith(SUFFIX) else folder


def generate():
    topics = []
    for folder in sorted(os.listdir(DOCS_DIR)):
        fdir = os.path.join(DOCS_DIR, folder)
        if not os.path.isdir(fdir):
            continue
        items = []
        files = [f for f in sorted(os.listdir(fdir)) if f.endswith('.md') and f != 'README.md']
        for fname in files:
            title = read_h1(os.path.join(fdir, fname)) or file_title(fname)
            rel = '面试知识库/%s/%s' % (folder, fname)
            items.append('      { %s = %s }' % (q(title), q(rel)))
        if os.path.isfile(os.path.join(fdir, 'README.md')):
            items.append('      { %s = %s }' % (q('总览'), q('面试知识库/%s/README.md' % folder)))
        if not items:
            continue
        topics.append('    { %s = [\n%s\n    ] }' % (q(section_title(folder)), ',\n'.join(items)))

    lines = ['nav = [', '  { %s = %s },' % (q('主页'), q('README.md')), '  { %s = [' % q('面试知识库')]
    for i, block in enumerate(topics):
        lines.append(block + (',' if i < len(topics) - 1 else ''))
    lines.append('  ] },')
    lines.append(']')
    return '\n'.join(lines) + '\n\n'


def main():
    new_nav = generate()
    with open(CONFIG, encoding='utf-8') as f:
        text = f.read()
    start = text.index('nav = [')
    end = text.index('[project.theme]')
    with open(CONFIG, 'w', encoding='utf-8') as f:
        f.write(text[:start] + new_nav + text[end:])
    print('nav 已更新')


if __name__ == '__main__':
    main()