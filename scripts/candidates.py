import json
import requests
from pathlib import Path

API_URL = "https://aihorde.net/api/v2/stats/img/models"

SCRIPT_DIR = Path(__file__).resolve().parent
CANDIDATE_PATHS = [
    (SCRIPT_DIR.parent / "stable_diffusion.json"),
    Path("../stable_diffusion.json"),
    Path("stable_diffusion.json"),
]

for path in CANDIDATE_PATHS:
    if path.is_file():
        REFERENCE_FILE = str(path.resolve())
        break
else:
    raise FileNotFoundError(
        "Could not find stable_diffusion.json in expected locations."
    )


def load_reference_models():
    with open(REFERENCE_FILE, "r") as file:
        reference_data = json.load(file)
    return set(reference_data.keys())


def process_model_stats():
    response = requests.get(API_URL)
    if response.status_code != 200:
        print(f"Failed to fetch data from API. Status code: {response.status_code}")
        return

    data = response.json()
    reference_models = load_reference_models()

    for period in ["day", "month", "total"]:
        stats = data[period]
        # Sort all models by usage
        sorted_stats = sorted(stats.items(), key=lambda x: x[1])
        print(f"{period.capitalize()} Lows")
        print("=" * 10)
        non_zero_count = 0
        for model, value in sorted_stats:
            output = f"{model}: {value}"
            if model not in reference_models:
                output += "\033[31m (not in reference)\033[0m"
                if value == 0:
                    # Skip models not in reference with zero usage
                    # These models have already been removed from the reference
                    # and are not relevant for candidates for removal
                    continue
            else:
                output += "\033[32m (in reference)\033[0m"
                if value == 0:
                    output += "\033[33m (zero usage)\033[0m"
            print(output)
            if value > 0:
                non_zero_count += 1
            if non_zero_count >= 10:
                break
        print()


if __name__ == "__main__":
    process_model_stats()
