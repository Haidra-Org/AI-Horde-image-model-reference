# Image Grid Template
Create image grids to showcase model capabilities to users of [Stable Horde](https://stablehorde.net/)
## Template

```
base image: 512x512
grid resolution: 1536x1536
grid format: webp
(3) or more prompt variations
```
Below are optional steps in case you are not familiar with photo editors; fairly simple way to create a image grid
Instructions
1. Paste the following code into the yaml text field
2. Load (9) images
3. Click *Generate*
4. Click *Save*

[Image Grid Generator](https://image-grid-generator.com/)
```yaml
fileName: image-grid.png
width: 1536
height: 1536
columns: 3
rows: 3
outerMargin:
  top: 0
  bottom: 0
  left: 0
  right: 0
innerMargin: 0
backgroundColorCode: '#FFFFFF00'
shadow:
  color: 'rgba(0, 0, 0, 0)'
  blur: 0
  offsetX: 0
  offsetY: 0

```

## Link showcase to Json
[AI-Horde-image-model-reference/db.json](../db.json)

```json
"Anything Diffusion": {
    "name": "Anything Diffusion",
    "type": "ckpt",
    "description": "Highly detailed Anime styled generations",
    "showcases": [
	"https://raw.githubusercontent.com/db0/AI-Horde-image-model-reference/main/showcase/anything_diffusion/01.webp"
	],
    "version": "3",
    "style": "anime",
```
## Example Image
Anything Diffusion
![alt text](https://github.com/db0/AI-Horde-image-model-reference/blob/main/showcase/anything_diffusion/01.webp "Anything Diffusion")

