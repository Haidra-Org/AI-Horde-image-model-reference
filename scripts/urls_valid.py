import argparse
import json
import time
from pathlib import Path
import requests

from loguru import logger

from horde_model_reference.legacy.classes.raw_legacy_model_database_records import (
    RawLegacy_StableDiffusion_ModelRecord,
    RawLegacy_DownloadRecord,
)


def urls_valid(
    sd_db: Path,
) -> bool:
    raw_json_sd_db: str
    with open(sd_db) as sd_db_file:
        raw_json_sd_db = sd_db_file.read()
    try:
        loaded_json_sd_db = json.loads(raw_json_sd_db)
    except Exception as e:
        logger.exception(e)
        logger.exception(f"ERROR: The stable diffusion database specified ({sd_db}) is not a valid json file.")
        if __name__ == "__main__":
            exit(1)
        else:
            return False

    parsed_db_records: dict[str, RawLegacy_StableDiffusion_ModelRecord] = {
        k: RawLegacy_StableDiffusion_ModelRecord.model_validate(v) for k, v in loaded_json_sd_db.items()
    }

    all_errors = []

    for model_name, model in parsed_db_records.items():
        for config_name, configs in model.config.items():
            if config_name == "download":
                if len(configs) == 0:
                    all_errors.append(f"Model {model_name} has no download URLs in the stable diffusion database.")
                    continue
                
                if len(configs) > 1 and "cascade" not in model_name.lower():
                    all_errors.append(f"Model {model_name} has multiple download URLs in the stable diffusion database. Only one is expected.")
                    continue

                download_entry = configs[0]

                if not isinstance(download_entry, RawLegacy_DownloadRecord):
                    all_errors.append(f"Model {model_name} has an invalid download entry in the stable diffusion database: {download_entry}. Expected RawLegacy_DownloadRecord.")
                    continue

                if not download_entry.file_url:
                    all_errors.append(f"Model {model_name} has an empty file_url in the stable diffusion database.")
                    continue

                if not download_entry.file_url.startswith("http"):
                    all_errors.append(f"Model {model_name} has an invalid file_url in the stable diffusion database: {download_entry.file_url}. It should start with 'http'.")
                    continue

                try:
                    response = requests.head(download_entry.file_url, allow_redirects=True)
                    time.sleep(0.1)
                    if response.status_code in [403, 524] and "civitai" in download_entry.file_url:
                        logger.error(f"Model {model_name} requires logging in to Civitai to access the download URL: {download_entry.file_url}.")
                        continue
                    if response.status_code != 200:
                        all_errors.append(f"Model {model_name} has an invalid URL: {download_entry.file_url}. Status code: {response.status_code}")
                        continue
                except requests.RequestException as e:
                    all_errors.append(f"Model {model_name} has an invalid URL: {download_entry.file_url}. Exception: {e}")
                    continue


    logger.info(f"Checked {len(parsed_db_records)} models in the stable diffusion database.")
    logger.info(f"Checked {sum(len(model.config.get('download', [])) for model in parsed_db_records.values())} download URLs.")

    if all_errors:
        logger.error("Some URLs in the stable diffusion database are invalid:")
        for error in all_errors:
            logger.error(f" - {error}")
        return False

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate URLs in the stable diffusion database.")
    parser.add_argument("sd_db", type=Path, help="Path to the stable diffusion database JSON file.")
    args = parser.parse_args()
    urls_valid(args.sd_db)
