import json
import sys
from git import Repo
from pathlib import Path
from typing import Dict, Optional


repo = Repo(Path(__file__).resolve(), search_parent_directories=True)
if repo.working_tree_dir is None:
    raise RuntimeError(
        "Could not determine the working tree directory for the git repository."
    )
repo_path = Path(repo.working_tree_dir)
file_path = "stable_diffusion.json"

# Gather all models ever present in the file's history
all_models_ever = set()
for commit in repo.iter_commits(paths=file_path):
    try:
        blob = commit.tree / file_path
        content = blob.data_stream.read().decode()
        data = json.loads(content)
        all_models_ever.update(data.keys())
    except Exception as e:
        # skip malformed commits (e.g., file missing, decode error); log for debugging
        print(f"Skipping commit {commit.hexsha}: {e}")
        continue

models_list = sorted(all_models_ever)

# Prepare tracking structure
model_mod_data: Dict[str, Dict[str, Optional[str | int]]] = {
    model: {
        "commit_added": None,
        "date_added": None,
        "commit_modified": None,
        "date_modified": None,
        "commit_removed": None,
        "date_removed": None,
    }
    for model in models_list
}

# Track previous data for each model to detect modifications
prev_model_data = {model: None for model in models_list}
present_last_commit = {model: False for model in models_list}

# Iterate commits from oldest to newest
commits = list(repo.iter_commits(paths=file_path))
for commit in reversed(commits):
    try:
        blob = commit.tree / file_path
        content = blob.data_stream.read().decode()
        data = json.loads(content)
    except Exception:
        # skip malformed commits
        continue

    for model in models_list:
        is_present = model in data
        if is_present:
            # Added
            if model_mod_data[model]["commit_added"] is None:
                model_mod_data[model]["commit_added"] = commit.hexsha
                model_mod_data[model]["date_added"] = int(
                    commit.committed_datetime.timestamp()
                )
                # First appearance should also be counted as a modification.
                model_mod_data[model]["commit_modified"] = commit.hexsha
                model_mod_data[model]["date_modified"] = int(
                    commit.committed_datetime.timestamp()
                )
            # Modified
            if prev_model_data[model] is not None and json.dumps(
                prev_model_data[model], sort_keys=True
            ) != json.dumps(data.get(model), sort_keys=True):
                model_mod_data[model]["commit_modified"] = commit.hexsha
                model_mod_data[model]["date_modified"] = int(
                    commit.committed_datetime.timestamp()
                )
            prev_model_data[model] = data[model]
            present_last_commit[model] = True
        else:
            # Removed
            if (
                present_last_commit[model]
                and model_mod_data[model]["commit_removed"] is None
            ):
                model_mod_data[model]["commit_removed"] = commit.hexsha
                model_mod_data[model]["date_removed"] = int(
                    commit.committed_datetime.timestamp()
                )
            prev_model_data[model] = None
            present_last_commit[model] = False

if "--check" in sys.argv:
    with open(repo_path / "model_mod_data.json") as f:
        existing = json.load(f)
    if existing != model_mod_data:
        print("model_mod_data.json is out of date. Run: python scripts/date_info.py")
        sys.exit(1)
    print("model_mod_data.json is up to date.")
else:
    with open(repo_path / "model_mod_data.json", "w") as f:
        json.dump(model_mod_data, f, indent=4)
