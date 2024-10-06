from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import json
import os
import hashlib
import requests
from tqdm import tqdm
import re

STYLE_OPTIONS = ["anime", "artistic", "furry", "generalist", "other", "realistic"]
ACTION_OPTIONS = ["add", "update", "remove"]
style_completer = WordCompleter(STYLE_OPTIONS, ignore_case=True)
baseline_completer = WordCompleter(
    [
        "stable diffusion 1",
        "stable diffusion 2",
        "stable_diffusion_xl",
        "stable_cascade",
        "flux_1",
    ],
    ignore_case=True,
)
action_completer = WordCompleter(ACTION_OPTIONS, ignore_case=True)


def load_models(json_file):
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            return json.load(f)
    return {}


def save_models(json_file, models):
    with open(json_file, "w") as f:
        json.dump(models, f, indent=4)


def download_and_get_size(url):
    response = requests.get(url, stream=True)
    if response.status_code == 401:
        print(
            "Model requires authorization to add, please add details to stable_diffusion.json manually."
        )
        return url, 1, "REPLACE_ME", ""

    total_size = int(
        response.headers.get("Content-Length", 0)
    )  # Total size of the file
    content_disposition = response.headers.get("Content-Disposition")

    if content_disposition:
        match = re.findall('filename="(.+)"', content_disposition)
        if match:
            file_name = match[0]
        else:
            file_name = url.split("/")[-1]
    else:
        file_name = url.split("/")[-1]

    file_size = 0
    sha256 = hashlib.sha256()
    file_path: Path = Path.cwd() / "tmp" / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)

    chunk_size = 8192
    with open(file_path, "wb") as f, tqdm(
        total=total_size, unit="B", unit_scale=True, desc=file_name
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:  # Filter out keep-alive chunks
                file_size += len(chunk)
                sha256.update(chunk)
                f.write(chunk)
                progress_bar.update(len(chunk))

    return file_name, file_size, sha256.hexdigest().upper(), file_path


def get_model_info():
    name = prompt("Model Name: ")
    baseline = prompt("Baseline: ", completer=baseline_completer)
    inpainting = prompt("Inpainting (t/f): ", default="false").lower()[0] == "t"
    description = prompt("Description: ")
    version = prompt("Version: ")
    style = prompt("Style (realistic, artistic, etc.): ", completer=style_completer)
    homepage = prompt("Homepage URL: ")
    nsfw = prompt("NSFW (t/f): ").lower()[0] == "t"

    url = prompt("Download URL: ")
    file_name, size_on_disk, sha256, file_path = download_and_get_size(url)
    if prompt("Delete downloaded model (t/f): ", default="t").lower()[0] == "t":
        os.remove(file_path)
    config = {
        "files": [{"path": file_name, "sha256sum": sha256}],
        "download": [{"file_name": file_name, "file_path": "", "file_url": url}],
    }

    return {
        "name": name,
        "baseline": baseline,
        "type": "ckpt",
        "inpainting": inpainting,
        "description": description,
        "version": version,
        "style": style,
        "homepage": homepage,
        "nsfw": nsfw,
        "download_all": False,
        "config": config,
        "size_on_disk_bytes": size_on_disk,
    }


def add_model(json_file):
    models = load_models(json_file)
    model = get_model_info()

    models[model["name"]] = model
    save_models(json_file, models)
    print(f"Model '{model['name']}' added successfully!")


def update_model(json_file):
    models = load_models(json_file)
    name = prompt("Model Name to update: ")

    if name not in models:
        print(f"Model '{name}' not found.")
        return

    model = get_model_info()
    models[name] = model
    save_models(json_file, models)
    print(f"Model '{name}' updated successfully!")


def remove_model(json_file):
    models = load_models(json_file)
    name = prompt("Model Name to remove: ")

    if name in models:
        del models[name]
        save_models(json_file, models)
        print(f"Model '{name}' removed successfully!")
    else:
        print(f"Model '{name}' not found.")


def main():
    json_file = "stable_diffusion.json"

    action = prompt(
        "Choose action (add/update/remove): ", completer=action_completer
    ).lower()[0]

    if action == "a":
        add_model(json_file)
    elif action == "u":
        update_model(json_file)
    elif action == "r":
        remove_model(json_file)
    else:
        print("Invalid action. Please choose from add, update, or remove.")


if __name__ == "__main__":
    main()
