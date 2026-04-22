这是将 Gemini Canvas 生成的代码转化为生产级、可在线访问的 GitHub Pages 项目的技术流程总结。

### 技术架构图
`Gemini Canvas (原型)` -> `Vite + React (本地工程化)` -> `Tailwind CSS (样式适配)` -> `GitHub Pages (自动化部署)`

---

### 核心流程文档：从 AI 原型到在线演示

#### 1. 环境初始化 (Scaffolding)
AI 生成的代码通常是单文件或片段。要使其运行，首先需要建立标准的 Web 开发环境。
*   **工具选择**：推荐使用 **Vite**，启动快且配置简单。
*   **执行命令**：
    ```bash
    npx create-vite@latest web-pre --template react
    cd web-pre
    npm install
    ```

#### 2. 补全依赖 (Dependencies)
Gemini Canvas 代码常引用一些现代库，必须手动安装到本地：
*   **Lucide React**：图标支持。
*   **Framer Motion**：平滑的 PPT 翻页动画。
*   **Tailwind CSS**：AI 最爱的样式框架（需初始化配置 `tailwind.config.js`）。
    ```bash
    npm install lucide-react framer-motion tailwindcss postcss autoprefixer
    npx tailwindcss init -p
    ```

#### 3. 代码重构与本地化 (Code Adaptation)
将 Canvas 里的代码“搬家”到 `src/App.jsx`。
*   **资源替换**：若 AI 生成了占位图，需替换为本地图片或真实 URL。
*   **模块拆分**：如果代码量大，将各个“幻灯片”逻辑拆分成独立的 Component 文件夹。
*   **样式注入**：确保 `index.css` 引入了 Tailwind 的三层指令。
*   **本地运行**：启动开发服务器： 运行以下命令：
    ```bash
    npm run dev
    ```

#### 4. 针对 GitHub Pages 的关键配置 (Critical Configuration)
这是最容易踩坑的一步，因为 GitHub Pages 默认部署在子路径（如 `username.github.io/repo-name/`）。
*   **Vite 配置**：在 `vite.config.js` 中设置 `base`。
    ```javascript
    export default defineConfig({
      base: '/your-repo-name/', // 必须与仓库名一致
      plugins: [react()],
    })
    ```
*   **路由适配**：如果使用了 `react-router`，需配置 `basename`。

#### 5. 自动化部署 (Deployment)
使用 `gh-pages` 脚本实现一键发布。
*   **安装工具**：`npm install gh-pages --save-dev`
*   **配置 Package.json**：
    ```json
    "scripts": {
      "predeploy": "npm run build",
      "deploy": "gh-pages -d dist"
    }
    ```
*   **发布**：执行 `npm run deploy`。

---

### 避坑指南 (Pro Tips)
1.  **Case Sensitivity**：Windows 不区分文件名大小写，但 GitHub Pages 的服务器（Linux）区分。确保 import 语句的大小写与实际文件完全匹配。
2.  **Asset Path**：在 React 代码中引用图片，尽量使用 `import img from './assets/xxx.png'`，这样 Vite 会自动处理 Base URL 路径。
3.  **404 问题**：如果使用了单页应用路由（SPA），刷新页面可能报错。解决方法是在 `public` 下放一个 `404.html` 重定向回 `index.html`。

### 总结
这个流程的核心价值在于：**利用 AI 解决“从 0 到 1”的创意产出，利用工程化工具解决“从 1 到 100”的稳定性与分发问题。**