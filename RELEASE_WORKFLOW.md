# Automated Release Workflow

This repository includes a GitHub Actions workflow that automatically builds and releases your Python package when you push version tags.

## How It Works

The workflow triggers on any tag that starts with `v` and performs the following steps:

1. **Extracts version** from the git tag (removes the `v` prefix)
2. **Updates `setup.py`** with the extracted version
3. **Builds the package** using `python -m build`
4. **Creates a GitHub release** with the tag
5. **Uploads build artifacts** (wheel, source distribution, checksums)

## Usage

### Creating a Release

1. **Tag your commit** with a version starting with `v`:
   ```bash
   git tag v1.9.20
   ```

2. **Push the tag** to trigger the workflow:
   ```bash
   git push origin v1.9.20
   ```

3. **Wait for the workflow** to complete (usually 2-3 minutes)

4. **Check the release** at: `https://github.com/text2everything_sdk/releases`

### Supported Tag Formats

The workflow accepts any tag starting with `v`:

- ✅ `v1.9.20` → Version: `1.9.20`
- ✅ `v0.1.5` → Version: `0.1.5`
- ✅ `v2.0.0-rc1` → Version: `2.0.0-rc1`
- ✅ `v1.5.0-alpha.1` → Version: `1.5.0-alpha.1`
- ✅ `v0.3.3-beta` → Version: `0.3.3-beta`
- ✅ `v1.0-hotfix` → Version: `1.0-hotfix`
- ❌ `1.9.20` (no `v` prefix)
- ❌ `release-1.0` (doesn't start with `v`)

### Pre-release Detection

The workflow automatically detects pre-releases based on the version string:
- Tags containing `-` (dash) are marked as pre-releases
- Examples: `v1.0.0-rc1`, `v2.0-alpha`, `v1.5.0-beta.2`

## What Gets Created

### GitHub Release
- **Title**: `Release v1.9.20`
- **Tag**: The exact tag you pushed
- **Description**: Auto-generated with package info and installation instructions
- **Assets**: All build artifacts and checksums

### Build Artifacts
- **Source Distribution**: `text2everything-sdk-1.9.20.tar.gz`
- **Wheel Distribution**: `text2everything_sdk-1.9.20-py3-none-any.whl`
- **Checksums**: `checksums.txt` with SHA256 hashes

## Example Workflow

```bash
# 1. Make your changes and commit
git add .
git commit -m "Add new feature for v1.9.20"

# 2. Create and push tag
git tag v1.9.20
git push origin v1.9.20

# 3. GitHub Actions automatically:
#    - Updates setup.py version to "1.9.20"
#    - Builds the package
#    - Creates release with artifacts
#    - Uploads to GitHub Releases

# 4. Users can now install:
pip install text2everything-sdk==1.9.20
```

## Troubleshooting

### Workflow Failed
1. Check the **Actions** tab in your GitHub repository
2. Look at the failed step's logs
3. Common issues:
   - Invalid tag format (must start with `v`)
   - Build dependencies missing
   - Syntax errors in `setup.py`

### Release Not Created
- Ensure you have the correct repository permissions
- Check that `GITHUB_TOKEN` has `contents: write` permission
- Verify the tag was pushed to the correct branch

### Version Not Updated
- The workflow uses `sed` to update the version in `setup.py`
- It looks for the pattern: `version="..."`
- Ensure your `setup.py` follows this format

## Workflow File Location

The workflow is defined in: `.github/workflows/release.yml`

## Permissions Required

The workflow needs these permissions (already configured):
- `contents: write` - To create releases and upload assets
- `id-token: write` - For trusted publishing (future PyPI integration)

## Future Enhancements

This workflow can be extended to:
- Automatically publish to PyPI
- Run tests before building
- Generate changelog from commits
- Send notifications to Slack/Discord
- Create Docker images

---

**Note**: This workflow only triggers on tag pushes, not regular commits. Your main branch remains unaffected by the automated version updates.
