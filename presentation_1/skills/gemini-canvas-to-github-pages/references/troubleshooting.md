# Troubleshooting

## 1) Blank page online
Possible causes:
- `base` is not set to `/<repo-name>/` in `vite.config.js`
- Missing dependencies
- Runtime error in source code

Suggested checks:
1. Run `npm run build` locally.
2. Open browser console and inspect the first error.
3. Confirm static asset requests include repository subpath.

## 2) Styles missing on Pages but fine locally
Possible causes:
- Tailwind directives are not included in global stylesheet
- Import path case mismatch (Linux is case-sensitive)

Suggestions:
- Verify `src/index.css` contains Tailwind base directives.
- Match import casing with actual file names.

## 3) 404 on refresh for subpages
Possible causes:
- Using `BrowserRouter` without `basename`

Suggestions:
- Configure router `basename=/<repo-name>/`
- Or add a `404.html` fallback strategy to `index.html`

## 4) Site not updated after manual publish
Possible causes:
- Browser cache still serves old files
- Latest `dist` content was not pushed to `gh-pages`
- `dist` folder itself was copied to root (should copy files inside `dist`)

Suggestions:
- Hard refresh (`Ctrl+F5`) or clear browser cache
- Check latest commit timestamp on `gh-pages`
- Ensure `index.html` is at branch root, not nested under `dist`

## 5) Deployment done but URL still 404
Possible causes:
- Wrong Pages source/branch/folder selection

Suggestions:
- In Settings > Pages, set `Deploy from a branch`
- Choose branch `gh-pages` and folder `/(root)`
