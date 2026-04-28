---
sidebar_position: 1
---

# 写作与发布流程

这个站点的推荐流程很简单：

1. 在 `blog/` 目录新增 Markdown 或 MDX 文件。
2. 本地运行 `npm run start` 预览。
3. 提交并推送到 `main` 分支。
4. GitHub Actions 自动构建并发布到 GitHub Pages。

适合长期维护的专题内容，可以放进 `docs/` 目录并在 `sidebars.js` 中加入导航。

