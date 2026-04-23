---
name: gemini-canvas-to-github-pages
description: '将 Gemini Canvas 或 AI 生成的 React 单文件原型工程化为可在线访问的 GitHub Pages 项目。适用于“把 html/react 原型发布到 Pages”“Vite + React + Tailwind 迁移”“配置 Pages 自动部署”“开源复现指南”场景。'
argument-hint: '仓库名、项目目录、是否使用自定义域名'
user-invocable: true
---

# Gemini Canvas To GitHub Pages

## 适用场景
- 你有一份 AI 生成的 React 代码（常见为单文件或伪 html），希望部署为公开网页。
- 你希望把流程写成可复现文档，便于课程作业、开源仓库或团队协作。
- 你需要稳定的自动化部署，而不是手工上传 dist 文件。

## 输入与前提
- 已有 GitHub 仓库。
- 本地可用 Node.js LTS 与 npm。
- 代码目标是 React 前端页面。

## 标准产物
- 前端工程目录（推荐 Vite + React）。
- 正确配置的 base 路径。
- GitHub Actions 部署工作流（发布到 Pages）。
- 可复用的排错文档与复现步骤。

## 执行流程
1. 识别代码类型。
如果文件包含 import React、JSX、第三方依赖（如 lucide-react），则这是 React 源码，不是可直接双击打开的静态 html。

2. 初始化工程。
在目标目录创建 Vite React 项目并安装依赖。
- 参考命令：
  - npx create-vite@latest web-pre --template react
  - cd web-pre
  - npm install

3. 迁移原型代码。
将核心页面逻辑迁移到 src/App.jsx，清理无效导入与未使用变量。

4. 补齐依赖。
按源码导入安装依赖（例如 lucide-react、framer-motion、tailwindcss）。

5. 配置 GitHub Pages 子路径。
在 vite.config.js 设置 base 为 /<repo-name>/，repo-name 必须和仓库名一致。

6. 本地验证。
- npm run dev：交互验证
- npm run build：构建验证

7. 配置自动部署。
在 .github/workflows/deploy-pages.yml 写入 Pages 工作流。
可直接使用模板 [deploy-pages.yml](./assets/deploy-pages.yml)。

8. 启用 Pages。
在仓库 Settings > Pages 中将 Source 设置为 GitHub Actions。

9. 输出复现信息。
在 README 或文档中记录：
- 运行命令
- 部署地址
- 常见问题与修复

## 质量检查清单
- 构建通过（npm run build 成功）
- 页面资源路径正确（刷新子路由不 404）
- 仓库中已有 .github/workflows/deploy-pages.yml
- Actions 执行成功并产生线上 URL

## 常见问题
- Windows 本地可运行但线上资源丢失：通常是路径大小写或 base 配置错误。
- 页面空白：检查控制台报错，多数为依赖未安装或导入路径错误。
- 刷新 404：若使用前端路由，补充 404 回退策略。

详细排错可见 [troubleshooting.md](./references/troubleshooting.md)。

## 开源复现建议
- 固定 Node 版本（例如在 README 说明 Node 20+）。
- 保留最小可运行示例与部署截图。
- 每次流程更新时同步维护模板与文档，确保新贡献者可以无痛复现。
