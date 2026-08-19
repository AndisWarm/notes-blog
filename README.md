# Zensical 知识文档站点

基于 [Zensical](https://zensical.org/)（Material for MkDocs 官方继任者）构建的 Markdown 文档平台，展示 `F:\知识库\豆瓣读书\学习笔记` 的后端面试知识文档。

## 使用

```powershell
# 1. 首次使用：安装依赖（一次性）
pip install deepmerge click jinja2 markdown pygments pymdown-extensions pyyaml tomli

# 2. 同步文档：把学习笔记复制到 docs/
powershell -ExecutionPolicy Bypass -File sync.ps1

# 3. 本地预览（http://localhost:8000）
$env:PYTHONPATH = "F:\知识库\博客网站集合\zensical-0.0.56-cp310-abi3-win_amd64"
python -m zensical serve

# 4. 构建静态站点（输出到 site/）
python -m zensical build
```

## 目录结构

- `zensical.toml` — 站点配置（站点名、导航 nav、主题、Markdown 扩展）
- `docs/` — 文档源（从学习笔记同步的副本，**排除** node_modules/.git）
- `site/` — 构建产物
- `sync.ps1` — 文档同步脚本（robocopy /MIR 镜像学习笔记 → docs）
- `gen_zensical_config.py` — nav 自动生成脚本（文档新增/改名后重跑，重新生成 zensical.toml 的 nav 部分）
- `zensical/` — zensical 包本体（本地解压版）

## 工作机制与注意事项

1. **文档为副本**：Zensical 0.0.56 的 Rust 核心要求 `docs_dir` 位于项目根内，且扫描器不跟随 Windows junction。因此 docs/ 是学习笔记的真实副本，编辑文档后运行 `sync.ps1` 重新同步（/MIR 镜像，保持与源一致）。
2. **新增文档**：在 `F:\知识库\豆瓣读书\学习笔记` 新建章节后，运行 `sync.ps1` 同步，再运行 `gen_zensical_config.py` 重新生成 nav。
3. **中文锚点**：站点配置了 `pymdownx.slugs.slugify` 以保留中文标题锚点（如 `#一先还原场景这段话在说什么`）。
4. **本地修改**：`zensical/config.py` 有两处本地补丁（允许绝对路径 docs_dir、外部目录时跳过 relative_to），当前配置使用项目内 `docs/` 不受影响，保留补丁以备将来直接指向外部目录。

## 参考

- [Zensical 中文教程](https://wcowin.work/Zensical-Chinese-Tutorial/)（Wcowin）
- [Zensical 官方文档](https://zensical.org/docs/)