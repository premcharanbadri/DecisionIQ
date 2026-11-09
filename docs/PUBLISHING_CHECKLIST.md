# Zero-cost GitHub Pages Deployment Checklist

- [ ] Make a public `decisioniq-copilot` repository.
- [ ] Commit the **contents** of the ZIP, not the ZIP itself.
- [ ] Confirm `/docs/index.html` exists on `main`.
- [ ] Confirm `/docs/lab/index.html` exists on `main`.
- [ ] Confirm `/docs/lab/assets/data.json` exists on `main`.
- [ ] Settings > Pages > Deploy from a branch > `main` > `/docs` > Save.
- [ ] Browse `https://YOUR_USERNAME.github.io/decisioniq-copilot/`.
- [ ] Click the static live lab; test budget and pricing controls.
- [ ] Confirm repo link navigates to your source.
- [ ] Run Python tests locally and record the result in the README if appropriate.
- [ ] Ensure no secrets, client data, or private account information exist in the repository.

**Do not describe this GitHub Pages site as a hosted frontier-model copilot.** The public page demonstrates deterministic browser analytics; the complete Python app runs separately.
