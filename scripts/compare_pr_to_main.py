import argparse
import json

from pathlib import Path

from horde_model_reference.legacy.classes.raw_legacy_model_database_records import (
    RawLegacy_StableDiffusion_ModelReference,
    RawLegacy_FileRecord,
    RawLegacy_StableDiffusion_ModelRecord,
)


def compare_pr_to_main(
    pr_path: Path,
    main_path: Path,
) -> tuple[
    dict[str, RawLegacy_StableDiffusion_ModelRecord],
    dict[str, RawLegacy_StableDiffusion_ModelRecord],
    dict[str, RawLegacy_StableDiffusion_ModelRecord],
]:
    with open(main_path) as main_sd_model_database_file:
        main_sd_model_database_file_contents = main_sd_model_database_file.read()

    main_sd_model_database_file_json = json.loads(main_sd_model_database_file_contents)
    main_model_reference = RawLegacy_StableDiffusion_ModelReference(
        root={
            k: RawLegacy_StableDiffusion_ModelRecord.model_validate(v)
            for k, v in main_sd_model_database_file_json.items()
        },
    )

    with open(pr_path) as pr_sd_model_database_file:
        pr_sd_model_database_file_contents = pr_sd_model_database_file.read()

    pr_sd_model_database_file_json = json.loads(pr_sd_model_database_file_contents)
    pr_model_reference = RawLegacy_StableDiffusion_ModelReference(
        root={
            k: RawLegacy_StableDiffusion_ModelRecord.model_validate(v)
            for k, v in pr_sd_model_database_file_json.items()
        },
    )

    models_added = {}
    models_removed = {}
    models_changed = {}
    models_changed_hashes: dict[str, tuple[str | None, str | None]] = {}

    for model_name, model in pr_model_reference.root.items():
        if model_name not in main_model_reference.root:
            models_added[model_name] = model
        else:
            pr_hash = None
            for _, pr_records in model.config.items():
                for pr_record in pr_records:
                    if (
                        isinstance(pr_record, RawLegacy_FileRecord)
                        and pr_record.sha256sum
                    ):
                        pr_hash = pr_record.sha256sum
                        break

            main_hash = None
            for _, main_records in main_model_reference.root[model_name].config.items():
                for main_record in main_records:
                    if (
                        isinstance(main_record, RawLegacy_FileRecord)
                        and main_record.sha256sum
                    ):
                        main_hash = main_record.sha256sum
                        break

            if pr_hash != main_hash:
                models_changed[model_name] = model
                models_changed_hashes[model_name] = (main_hash, pr_hash)

    for model_name, model in main_model_reference.root.items():
        if model_name not in pr_model_reference.root:
            models_removed[model_name] = model

    return models_added, models_removed, models_changed


def write_changes_to_dir(
    models_added: dict[str, RawLegacy_StableDiffusion_ModelRecord],
    models_removed: dict[str, RawLegacy_StableDiffusion_ModelRecord],
    models_changed: dict[str, RawLegacy_StableDiffusion_ModelRecord],
    output_dir: Path,
    pr_hash: str,
    main_hash: str,
):

    subdir_name = f"{main_hash[:8]}...{pr_hash[:8]}"
    output_dir = output_dir / subdir_name
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "models_added.json", "w") as models_added_file:
        json.dump(
            {k: v.model_dump() for k, v in models_added.items()},
            models_added_file,
            indent=4,
        )
        models_added_file.write("\n")

    with open(output_dir / "models_removed.json", "w") as models_removed_file:
        json.dump(
            {k: v.model_dump() for k, v in models_removed.items()},
            models_removed_file,
            indent=4,
        )
        models_removed_file.write("\n")

    with open(output_dir / "models_changed.json", "w") as models_changed_file:
        json.dump(
            {k: v.model_dump() for k, v in models_changed.items()},
            models_changed_file,
            indent=4,
        )
        models_changed_file.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr_path", type=Path)
    parser.add_argument("--main_path", type=Path)
    parser.add_argument("--pr_hash", type=str)
    parser.add_argument("--main_hash", type=str)
    parser.add_argument("--output_dir", type=Path)
    parser.add_argument("--info_file_out", type=Path, required=False)
    args = parser.parse_args()

    pr_path = args.pr_path
    main_path = args.main_path
    pr_hash = args.pr_hash
    main_hash = args.main_hash
    output_dir = args.output_dir

    models_added, models_removed, models_changed = compare_pr_to_main(
        pr_path, main_path
    )
    hash_compared = f"{main_hash[:8]}...{pr_hash[:8]}"

    output = ""
    info_file_out = args.info_file_out or f"pr_diff_{hash_compared}.txt"

    if len(models_added) == 0 and len(models_removed) == 0 and len(models_changed) == 0:
        output = f"No changes found between {hash_compared}"
    else:
        output = f"Models added from {hash_compared}:\n"
        for model_name, model in models_added.items():
            output += f"  + {model_name} v{model.version} ({model.baseline})\n"
            output += f"    {model.description}\n"
            output += f"    nsfw: {model.nsfw}\n"
            if model.inpainting:
                output += f"    Inpainting: {model.inpainting}\n"
            output += f"    {model.homepage}\n"
            output += f"    {model.tags}\n"
            output += "\n"

        output += "Models removed:\n"
        for model_name, model in models_removed.items():
            output += f"  - {model_name}\n"

        output += "Models changed:\n"
        for model_name, model in models_changed.items():
            output += f"  ~ {model_name}\n"

        if output_dir:
            if not pr_hash or not main_hash:
                raise ValueError(
                    "Must provide both pr_hash and main_hash to write changes to disk"
                )
            write_changes_to_dir(
                models_added,
                models_removed,
                models_changed,
                output_dir,
                pr_hash,
                main_hash,
            )

    print(output)

    with open(info_file_out, "w") as file:
        file.write(output)


if __name__ == "__main__":
    main()
