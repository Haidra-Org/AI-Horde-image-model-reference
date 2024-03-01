from pathlib import Path
from horde_model_reference.legacy.validate_sd import validate_legacy_stable_diffusion_db

if not validate_legacy_stable_diffusion_db(
    Path("stable_diffusion.json"),
    fail_on_extra=True,
):
    exit(1)
