# AGENTS.md

## Context and Lessons Learned

### Dependency Management
- **Issue**: `ModuleNotFoundError` when running a new script that requires packages listed in `requirements.txt`.
- **Context**: Updating `requirements.txt` does not automatically install the packages in the environment.
- **Action**: Always run `pip install -r requirements.txt` (or specific packages) in the active virtual environment after modifying `requirements.txt` and before running code that depends on the new packages.
