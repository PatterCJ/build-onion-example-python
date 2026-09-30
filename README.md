# build-onion example: Python

A small Python CLI built, independently reproduced, sealed and published by [build-onion](https://github.com/PatterCJ/build-onion). Nothing here is Python-specific to build-onion: the same three workflows build any language from a manifest.

## What's in the repo

| File | Role |
|---|---|
| [`build-onion.yml`](build-onion.yml) | The declared build: pinned builder image, lockfile, fetch (behind an egress allow-list), offline build, image output. |
| [`requirements.txt`](requirements.txt) | Hash-pinned lockfile, exported from `uv.lock`. |
| [`Dockerfile`](Dockerfile) | Assembles the image from what the offline build installed; nothing is fetched here. |
| [`.github/workflows/release.yml`](.github/workflows/release.yml) | On a signed `v*` tag: calls build-onion's build, security and publish lines, and records a `pip-audit` scan against the exact source snapshot. |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | On every pull request: runs build-onion's build line. Nothing is signed. |
| [`.build-onion/policy.yml`](.build-onion/policy.yml) | Release rules: only tags signed with the pyonion release key, required build inputs, repository protections. |

## Releasing

Merge to `main` (the pull request has already run the build line), then push a tag of `main` signed with the pyonion release key:

```sh
git fetch origin && git tag -s v0.1.2 -m "pyonion v0.1.2" origin/main && git push origin v0.1.2
```

The pushed tag starts the release; the gate blocks it unless the signing key is in `.build-onion/policy.yml`. Approve the publish job when it asks.

## What happens on a release

1. **Build line:** snapshot every source file, check pins, gate the release, fetch wheels through the egress proxy (only `pypi.org` and `files.pythonhosted.org`), and install them with no network.
2. **Scan:** `pip-audit` runs against the locked requirements, and its run is recorded against the source snapshot.
3. **Security line:** rebuild independently, require byte-identical output, generate the SBOM, and seal.
4. **Publish line:** after approval, peel the image, compare it with the previous release, and push it by digest.

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
