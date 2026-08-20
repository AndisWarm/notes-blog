# -*- coding: utf-8 -*-
"""根据 docs/ 的目录结构自动生成 zensical.toml 里的 nav 配置。

规则：
- docs/ 下每个一级目录（面试知识库、项目实战知识库…）成为导航的一级分组；
- 目录内 .md 文件（按文件名排序）成为文章，README.md 固定为「总览」排在末尾；
- 子目录递归展开为嵌套分组；
- 分组标题：优先用 FOLDER_TITLES 里的中文映射，其次去掉「面试知识讲解」后缀，其余保持原名。

用法：python gen_zensical_config.py
"""
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE, 'docs')
CONFIG = os.path.join(BASE, 'zensical.toml')

# 目录名 → 导航标题（未命中的目录走下面的后缀规则 / 保持原名）
FOLDER_TITLES = {
    'lightweight-ip-traffic-sa': '轻量 IP 态势感知系统',
    'docs': '开发文档',
    'learning': '学习路径',
    'learning-interview': '面试讲解',
    'manual': '使用手册',
    'reports': '测试报告',
    'test-results': '测试结果',
    'docs-小白补充包': '小白补充包',
    'learning-小白补充包': '学习小白补充包',
    'manual-beginner': '零基础手册',
}

# docs/ 下不参与导航的目录
IGNORE_DIRS = {'assets', 'javascripts', 'stylesheets', 'node_modules', '.git'}

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


def group_title(folder):
    if folder in FOLDER_TITLES:
        return FOLDER_TITLES[folder]
    if folder.endswith(SUFFIX):
        return folder[: -len(SUFFIX)]
    return folder


def build_tree(rel_dir):
    """递归构建一个目录的 nav 树。

    返回 [(kind, title, value), ...]：kind 为 'group' 时 value 是子列表，
    kind 为 'item' 时 value 是相对 docs/ 的路径。
    """
    abs_dir = os.path.join(DOCS_DIR, rel_dir)
    nodes = []
    for name in sorted(os.listdir(abs_dir)):
        if os.path.isdir(os.path.join(abs_dir, name)):
            children = build_tree('%s/%s' % (rel_dir, name))
            if children:
                nodes.append(('group', group_title(name), children))
    for name in sorted(os.listdir(abs_dir)):
        if name.endswith('.md') and name != 'README.md':
            path = os.path.join(abs_dir, name)
            title = read_h1(path) or file_title(name)
            nodes.append(('item', title, '%s/%s' % (rel_dir, name)))
    if os.path.isfile(os.path.join(abs_dir, 'README.md')):
        nodes.append(('item', '总览', '%s/README.md' % rel_dir))
    return nodes


def render(nodes, level):
    """把 nav 树渲染成 TOML 片段（每行一个字符串，同级元素逗号分隔）。"""
    lines = []
    pad = '  ' * level
    last = len(nodes) - 1
    for idx, (kind, title, value) in enumerate(nodes):
        comma = '' if idx == last else ','
        if kind == 'item':
            lines.append('%s{ %s = %s }%s' % (pad, q(title), q(value), comma))
        else:
            lines.append('%s{ %s = [' % (pad, q(title)))
            lines.extend(render(value, level + 1))
            lines.append('%s] }%s' % (pad, comma))
    return lines


def generate():
    nav_nodes = [('item', '主页', 'README.md')]
    for name in sorted(os.listdir(DOCS_DIR)):
        if name in IGNORE_DIRS:
            continue
        if not os.path.isdir(os.path.join(DOCS_DIR, name)):
            continue
        tree = build_tree(name)
        if tree:
            nav_nodes.append(('group', group_title(name), tree))

    lines = ['nav = [']
    lines.extend(render(nav_nodes, 1))
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