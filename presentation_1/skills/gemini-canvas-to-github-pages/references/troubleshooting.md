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

## 4) Actions 构建失败
可能原因：
- 工作流中的 working-directory 与项目实际路径不一致
- lock 文件不存在却使用 npm ci

建议：
- 若无 package-lock.json，先本地 npm install 并提交 lock 文件
- 校正工作流中的路径到真实工程目录

## 5) 部署成功但访问 404
可能原因：
- 仓库 Settings > Pages 未设置为 GitHub Actions

建议：
- 手动进入仓库设置，确认 Source 为 GitHub Actions
- 重新触发一次 workflow_dispatch
