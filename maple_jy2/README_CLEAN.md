# maple_jy cleaned package

This is a cleaned copy made from `C:\git\maple_jy.zip`.

## What was kept

- Python source files and helper scripts.
- Runtime templates under `templates/`.
- Runtime captcha assets under `captcha_assets/`.
- Shop sample asset under `shop_assets/`.
- `.gitignore` and `.gitattributes`.

## What was removed

- The embedded `.git/` directory.
- Backup/original asset folders: `captcha_assets_orig/`, `templates_orig/`.
- Large captcha analysis screenshots such as `analysis_full_*`, `full_*`,
  `truth_full_*`, and `visual_full_*`.
- Backup image files such as `*.bak_*`.

## Small compatibility cleanup

- Updated macro variants that referenced `captcha_assets/con.png.png` to use
  `captcha_assets/con_.png.png`. On Windows, `con.png.png` cannot be created
  normally because `CON` is a reserved device name.
- Added missing runtime dependencies to `requirements.txt`: `pyautogui` and
  `Pillow`.

## Main files

- `macro_red.py`: largest/current-looking macro variant.
- `macro.py`, `macro_v2.py`, `macro_red_v1.py`, `macro_red_2kill.py`:
  older or alternate variants.
- `minimap_setup.py`, `minimap_setup_red.py`: minimap calibration tools.
- `mm_probe.py`, `mm_probe_red.py`, `ui_probe.py`: coordinate/probe helpers.
- `captcha_solver.py`, `focused_solver.py`: slider popup solver utilities.

Original archive was not modified.
