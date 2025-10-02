
# JupyterLite Dashboard (No Voilà/Voici)

A fully client-side dashboard that runs **entirely in the browser** via JupyterLite (Pyodide).
- Dynamic filtering (ipywidgets)
- Multiple plots (matplotlib)
- No server, no Voilà/Voici
- Synthetic dataset with tuning curves for 400 units

## Quick start (locally)

1. Install the JupyterLite CLI:
   ```bash
   pipx install jupyterlite==0.6.4
   # or
   pip install jupyterlite==0.6.4
   ```

2. Build the site:
   ```bash
   jupyter lite build --contents content --output-dir _output --base-url /
   python -m http.server -d _output  # serve locally
   ```

3. Open in your browser:
   - `http://localhost:8000/notebooks/?path=App.ipynb` (single-notebook app)
   - or JupyterLab: `http://localhost:8000/lab/index.html?path=App.ipynb`

## Deploy to GitHub Pages

1. Push this repo to GitHub.
2. Ensure GitHub Pages is set to deploy from the `gh-pages` branch.
3. Keep the provided workflow `.github/workflows/jupyterlite.yml` as-is.

After the first run, your site will be published at:
```
https://<your-username>.github.io/<repo-name>/
```
Direct dashboard link (single-notebook app):
```
https://<your-username>.github.io/<repo-name>/notebooks/?path=App.ipynb
```

> Note: This project hides notebook code cells by default. You can reveal them in JupyterLab if needed.

## Dataset

`content/data/units.json` includes
- `orientations`: 36 angles (0..350°, step 10)
- For each unit: layer (SG/G/IG), group (MUL/MXH), control/laser tuning (36 samples each),
  OSI, half-bandwidth, means, peak orientation.

## Advanced function patterns

See `content/py/utils.py` for examples mirroring MATLAB's `arguments` style via:
- keyword-only parameters
- positional-only parameters
- dataclass-based "arguments" container
- validation and simple helper utilities

Enjoy!
