---
name: gemini-canvas-to-github-pages
description: 'Convert Gemini Canvas or AI-generated React prototypes into production-ready GitHub Pages sites. Use for html/react prototype publishing, Vite + React + Tailwind migration, manual Pages deployment, and open-source reproducibility.'
argument-hint: 'Repository name, project directory, custom domain (optional)'
user-invocable: true
---

# Gemini Canvas To GitHub Pages (Manual Deployment)

## When To Use
- You have AI-generated React code (often a single file or pseudo-HTML) and want to publish it online.
- You want a reproducible process for coursework, open-source sharing, or team collaboration.
- You prefer a workflow-free setup with manual deployment.

## Inputs And Preconditions
- A GitHub repository is already created.
- Node.js LTS and npm are available locally.
- Target code is a React frontend.

## Expected Outputs
- A Vite + React project structure.
- Correct GitHub Pages base path configuration.
- A manual deployment strategy using branch and folder selection.
- Reusable troubleshooting and reproducibility notes.

## Procedure
1. Identify the code type.
If the file contains `import React`, JSX, or dependencies like `lucide-react`, it is React source code, not directly runnable static HTML.

2. Initialize project scaffolding.
Create a Vite React app and install dependencies.
- Example commands:
  - npx create-vite@latest web-pre --template react
  - cd web-pre
  - npm install

3. Migrate prototype code.
Move the page logic into `src/App.jsx` and remove unused imports/variables.

4. Install required dependencies.
Install all packages referenced by imports (for example, `lucide-react`, `framer-motion`, `tailwindcss`).

5. Configure GitHub Pages subpath.
Set `base` in `vite.config.js` as `/<repo-name>/` where `repo-name` must exactly match the GitHub repository name.

6. Validate locally.
- `npm run dev` for interaction checks
- `npm run build` for production build checks

7. Publish build artifacts manually.
Use a `gh-pages` branch to keep source code clean:
- Run `npm run build` to generate `dist`.
- Create and switch to `gh-pages` (or switch if it already exists).
- Clear old branch content, then copy files from inside `dist` to branch root.
- Commit and push `gh-pages`.

8. Enable GitHub Pages.
In repository Settings > Pages:
- Source: `Deploy from a branch`
- Branch: `gh-pages`
- Folder: `/(root)`

9. Document reproducibility.
In README or docs, record:
- Run/build commands
- Final site URL
- Common issues and fixes

## Quality Checklist
- Build succeeds (`npm run build`)
- Asset paths are correct (no 404 on refresh)
- `gh-pages` branch contains built files
- Pages is configured to `gh-pages /(root)` and site is accessible

## Common Issues
- Works locally but assets fail online: usually base path or case-sensitivity mismatch.
- Blank page: often missing dependencies or broken import paths.
- Refresh 404: configure router basename or fallback strategy.

See detailed troubleshooting: [troubleshooting.en.md](./references/troubleshooting.en.md).

## Open-Source Repro Tips
- Pin Node version in README (for example, Node 20+).
- Keep a minimal runnable sample and deployment screenshot.
- Update docs and templates together whenever the process changes.
