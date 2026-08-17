## CG Production Asset Downloader

### Batch download open source assets from Blender Studio

This script can be used to batch download assets from Blender Studio. While their assets are open source, Blender asks that you have a subscription to Blender Studio to download files. If you intend to use this script, please be sure to get a subscription to support the work being done byBlender. [Blender Studio](https://studio.blender.org/)

This script is not affiliated with Blender or Blender Studio. All assets downloaded are created by Blender Studio and available under the [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) license.

## Usage

1. Copy `.env.example` to `.env` and set `USER_COOKIE` there (see the screenshot below for how to find it). `.env` is gitignored, so it never gets committed.
2. Run the script, passing the gallery URL you want to download assets from:

```
python download_assets.py https://studio.blender.org/projects/<project>/<gallery-id>/
```

By default assets are saved to `cg-production-data/<project-name>/`. Pass `--dir` to save somewhere else:

```
python download_assets.py https://studio.blender.org/projects/<project>/<gallery-id>/ --dir "cg-production-data/shows/caminandes_llamigos/vr_demo/"
```

![USER_COOKIE](images/user_cookie.png)
