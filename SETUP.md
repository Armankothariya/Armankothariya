# Arman Kothariya — animated GitHub profile

## 1. Create or reuse the profile repository

The repository must be named exactly `Armankothariya` and be public.

If it already contains your current README, copy the files from this folder into that repository instead of creating another repository.

## 2. Generate the portrait once

Place your chosen photo in the repo root as `source-photo.jpg`.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r scripts/requirements.txt
python scripts/prep_photo.py source-photo.jpg
python scripts/make_ascii_svg.py
```

## 3. Generate the card and heatmap

```bash
python scripts/make_info_card.py
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
```

## 4. Commit the generated assets

Commit these files:

- `README.md`
- `typing-header.svg`
- `avi-ascii.svg`
- `info-card.svg`
- `contrib-heatmap.svg`
- `data/contributions.json`
- `scripts/*.py`
- `scripts/requirements.txt`
- `.github/workflows/update-profile-art.yml`

Do **not** commit `source-photo.jpg` or `source-prepped.png` unless you intentionally want the source image public.

## 5. Run the workflow

Open GitHub → Actions → **Update profile art** → **Run workflow**.

The workflow only installs `requests` and `beautifulsoup4`; it does not need the portrait packages.

## 6. Before you publish

Review the content in `scripts/make_info_card.py` and `README.md` so every status/role/project description still matches your current work.
