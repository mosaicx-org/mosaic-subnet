
from io import BytesIO
from typing import Optional
import base64

import torch
from diffusers import AutoPipelineForText2Image

from communex.module.module import Module, endpoint

class DiffUsers(Module):
    def __init__(self, model_name: str = "stabilityai/sdxl-turbo") -> None:
        super().__init__()
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "mps")
        self.pipeline = AutoPipelineForText2Image.from_pretrained(
            model_name, torch_dtype=torch.float16, variant="fp16"
        ).to(self.device)

    @endpoint
    def sample(
        self, prompt: str, steps: int = 50, negative_prompt: str = "", seed:
    Optional[int]=None) -> str:
        generator = torch.Generator(self.device)
        if seed is None:
            seed = generator.seed()
        generator = generator.manual_seed(seed)
        image = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            generator=generator,
            guidance_scale=0.0
        ).images[0]
        buf = BytesIO()
        image.save(buf, format="png")
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()

    @endpoint
    def get_metadata(self) -> dict:
        return {"model": self.model_name}

if __name__ == "__main__":
    d = DiffUsers()
    out = d.sample(prompt="cat, jumping")
    with open("a.png", "wb") as f:
        f.write(out)
