# Module Configuration Guide

This document explains how to configure a PrismQ module for automatic synchronization with its remote repository.

## Overview

Each PrismQ module can be synchronized with its own Git repository using the `sync-modules` scripts. Configuration is done through a `module.json` file in the module's root directory.

## Configuration File: `module.json`

### Location
Place the `module.json` file in the root directory of your module:
```
src/YourModule/
├── module.json          ← Configuration file
├── src/
├── tests/
└── README.md
```

### Format

The `module.json` file uses a simple JSON structure:

```json
{
  "remote": {
    "url": "https://github.com/YourOrg/YourRepo.git"
  }
}
```

### Required Fields

- **`remote.url`**: The Git repository URL for this module
  - Must be a valid Git repository URL
  - Can use HTTPS or SSH format
  - Should end with `.git`

### Auto-Generated Values

The sync scripts automatically derive the following values:

1. **Remote Name**: Generated from the repository URL
   - Extracted from the last part of the URL
   - Converted to lowercase
   - Dots (`.`) and underscores (`_`) replaced with hyphens (`-`)
   - Example: `PrismQ.RepositoryTemplate.git` → `prismq-repositorytemplate`

2. **Branch**: Always uses `main`
   - The main branch is the default sync target
   - Cannot be customized per design

## Examples

### Example 1: Standard GitHub Repository
```json
{
  "remote": {
    "url": "https://github.com/Nomoos/PrismQ.RepositoryTemplate.git"
  }
}
```
- **Derived remote name**: `prismq-repositorytemplate`
- **Branch**: `main`

### Example 2: Organization Repository
```json
{
  "remote": {
    "url": "https://github.com/MyOrg/MyProject.Core.git"
  }
}
```
- **Derived remote name**: `myproject-core`
- **Branch**: `main`

### Example 3: SSH Format
```json
{
  "remote": {
    "url": "git@github.com:Nomoos/PrismQ.IdeaInspiration.git"
  }
}
```
- **Derived remote name**: `prismq-ideainspiration`
- **Branch**: `main`

## Setting Up a New Module

### 1. Create the Module Directory Structure
```bash
mkdir -p src/YourModule/src
mkdir -p src/YourModule/tests
```

### 2. Create `module.json`
```bash
cat > src/YourModule/module.json << 'EOF'
{
  "remote": {
    "url": "https://github.com/YourOrg/YourRepo.git"
  }
}
EOF
```

### 3. Verify Configuration
Run the sync script to verify your module is discovered:

**Windows:**
```batch
scripts\sync-modules.bat --list
```

You should see your module listed with its auto-generated remote name.

### 4. Sync the Module
**Windows:**
```batch
scripts\sync-modules.bat src\YourModule
```

## How It Works

### Module Discovery
1. Scripts scan `src/*/` directories
2. Check for directories with both:
   - A `src/` subdirectory (indicating a valid module)
   - A `module.json` file
3. Parse `module.json` to extract the remote URL
4. Auto-generate remote name from URL
5. Add module to sync list

### Git Origin Management
When syncing a module:
1. Script reads `module.json` to get the remote URL
2. If the module directory has a `.git` folder:
   - Checks if `origin` remote exists
   - If not, adds it: `git remote add origin <url>`
   - If it exists but differs, updates it: `git remote set-url origin <url>`

### Synchronization Process
1. Adds/updates the git remote (e.g., `prismq-repositorytemplate`)
2. Fetches from remote: `git fetch <remote-name> main`
3. Pulls updates using git subtree: `git subtree pull --prefix=<module-path> <remote-name> main --squash`

## Troubleshooting

### Warning: module.json not found
**Cause**: The module directory exists but has no `module.json` file.

**Solution**: Create a `module.json` file in the module root with the remote URL.

### Warning: module.json is missing remote URL
**Cause**: The `module.json` file exists but doesn't have a valid `remote.url` field.

**Solution**: Ensure your JSON is valid and includes:
```json
{
  "remote": {
    "url": "https://github.com/..."
  }
}
```

### Module Not Discovered
**Cause**: Module might not have a `src/` subdirectory.

**Solution**: Ensure your module structure includes:
```
src/YourModule/
├── module.json
└── src/              ← Required
```

## Migration from REMOTE.md

If you're migrating from the old `REMOTE.md` format:

1. **Create `module.json`** with just the URL:
   ```json
   {
     "remote": {
       "url": "https://github.com/YourOrg/YourRepo.git"
     }
   }
   ```

2. **Remove `REMOTE.md`** (optional, but recommended)

3. **Test the configuration**:
   ```batch
   scripts\sync-modules.bat --list
   ```

The remote name will be auto-generated from the URL, which may differ from your old manual remote name. This is expected behavior.

## Best Practices

1. **Use HTTPS URLs** for public repositories (easier authentication)
2. **Keep it simple**: Let the scripts auto-generate the remote name
3. **Always sync from main**: The design enforces this for consistency
4. **Commit `module.json`**: This file should be version-controlled
5. **Validate JSON**: Use a JSON validator to ensure proper formatting

## Additional Resources

- [Git Subtree Documentation](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)
- [PrismQ Module Sync Scripts](../scripts/README.md)
- [Main PrismQ Repository](https://github.com/Nomoos/PrismQ)

---

**Note**: This configuration format is designed for simplicity and consistency. Remote names are auto-generated and branches are always `main` by design.
