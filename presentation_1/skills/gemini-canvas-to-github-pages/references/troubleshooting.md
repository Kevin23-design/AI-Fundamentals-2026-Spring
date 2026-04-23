# Troubleshooting

## 1) 线上空白页
可能原因：
- vite.config.js 的 base 未设置为 /仓库名/
- 依赖未安装完整
- 源码中存在运行时报错

排查顺序：
1. 本地执行 npm run build 确认可构建。
2. 打开浏览器控制台查看首个报错。
3. 确认静态资源请求路径包含仓库名。

## 2) 本地正常，Pages 样式丢失
可能原因：
- Tailwind 未注入到全局样式
- import 路径大小写在 Linux 下不匹配

建议：
- 检查 src/index.css 是否包含 tailwind 基础指令。
- 对照实际文件名修复大小写。

## 3) 刷新子页面 404
可能原因：
- 使用 BrowserRouter 但未配置 basename

建议：
- Router 使用 basename=/仓库名/
- 或增加 404 回退到 index.html 方案

## 4) 手动发布后页面未更新
可能原因：
- 浏览器缓存命中旧资源
- gh-pages 分支未推送最新 dist 内容
- 误把 dist 文件夹整体复制到了根目录（应复制 dist 内部文件）

建议：
- 强制刷新页面（Ctrl+F5）或清理缓存后重试
- 检查 gh-pages 分支最新提交时间是否更新
- 确认分支根目录直接包含 index.html，而不是嵌套在 dist 下

## 5) 部署成功但访问 404
可能原因：
- 仓库 Settings > Pages 的 Source 或分支选择错误

建议：
- 手动进入仓库设置，确认 Source 为 Deploy from a branch
- 分支选择 gh-pages，目录选择 /(root)
