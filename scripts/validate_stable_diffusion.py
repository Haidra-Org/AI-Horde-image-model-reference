from pathlib import Path
from horde_model_reference.legacy.validate_sd import validate_legacy_stable_diffusion_db

if not validate_legacy_stable_diffusion_db(Path("stable_diffusion.json")):
    exit(1)
