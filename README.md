# AI Horde image model reference

Model reference for [AIHorde](https://aihorde.net) [Worker](https://github.com/Haidra-Org/horde-worker-reGen).

## Notes to maintainers

- See https://github.com/Haidra-Org/horde-model-reference#horde-moderatorssupport-staff. Note that the venv the worker is installed in has `horde-model-reference` already installed.
- Always use `.safetensors` files
- Models added must always have an embedded VAE.
- Always test that the worker can load the models. You can request the `customizer` role from the horde admins in discord.
- Models which can readily be reproduced by a base model + LoRa should be avoided.
- Double check if the model has trigger words or a specific parameter requirement, such as `clip_skip: 2`.
- Be sure that you select the **pruned** version of a model, if it exists.
  - The pruned version of models only remove training data. This has no impact on the horde, however, unpruned models are typically much larger.
- Models selected from civitai should have extra care to be taken:
  - The download URL should be fully qualified and include all of the query data, such as
    - `?type=Model&format=SafeTensor&size=pruned&fp=fp16`
  - When selecting a version, try and prefer models which require fewer steps (such as lightning models) and those model versions which are shown to be popular.
  - Double, triple, and quadrple check that the SHA you've specified in the json matches the model type and format URL you've chosen.
- When adding large numbers of models, please strongly consider also proposing removing certain low usage models.
- When removing models, please also consider if the model may simply be niche but still useful. Low usage alone is not a disqualifier for inclusion on the model list.
- If your model change affects a top 10 model (by changing it or removing it, metadata-only changes for accuracy are alwasys OK), you must go through the [consensus process on loomio](https://loomio.haidra.net/) in order for that change to be accepted.
