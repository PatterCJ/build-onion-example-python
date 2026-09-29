# build-onion example: Python

A small Python CLI built, independently reproduced, sealed and published by [build-onion](https://github.com/PatterCJ/build-onion). Nothing here is Python-specific to build-onion: the same three workflows build any language from a manifest.

## What's in the repo

| File | Role |
|---|---|
| [`build-onion.yml`](build-onion.yml) | The declared build: pinned builder image, lockfile, fetch (behind an egress allow-list), offline build, image output. |
| [`requirements.txt`](requirements.txt) | Hash-pinned lockfile, exported from `uv.lock`. |
| [`Dockerfile`](Dockerfile) | Assembles the image from what the offline build installed; nothing is fetched here. |
| [`.github/workflows/release.yml`](.github/workflows/release.yml) | Calls build-onion's build, security and publish lines, and records a `pip-audit` scan against the exact source snapshot. |

## What happens on every push to `main`

1. **Build line:** snapshot every source file, check pins, gate the release, fetch wheels through the egress proxy (only `pypi.org` and `files.pythonhosted.org`), and install them with no network.
2. **Scan:** `pip-audit` runs against the locked requirements, and its run is recorded against the source snapshot.
3. **Security line:** rebuild independently, require byte-identical output, generate the SBOM, and seal.
4. **Publish line:** after approval, peel the image and push it by digest.

## Verify the image

```sh
onion peel ghcr.io/pattercj/build-onion-example-python@sha256:… \
  --repo PatterCJ/build-onion-example-python --packages
```

Every package in the image is proven against `requirements.txt`: `rich`, `PyYAML` and their dependencies by name and version, plus the Python base image's own packages by the pinned base's layers.

## Keeping it reproducible

- `pip install --no-compile --no-cache-dir` writes no bytecode or cache, so two installs are byte-identical.
- Wheels only (`--only-binary=:all:`): nothing is compiled during fetch.
- The image copies the installed tree onto a base pinned by digest; build-onion rewrites timestamps to the commit time.

## Updating dependencies

```sh
uv lock --upgrade
uv export --format requirements-txt --no-emit-project --no-dev -o requirements.txt
```
