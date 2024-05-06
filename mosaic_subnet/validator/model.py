from io import BytesIO

import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from transformers import pipeline
from loguru import logger

from communex.module.module import Module, endpoint


class CLIP(Module):
    def __init__(self, model_name: str = "laion/CLIP-ViT-L-14-laion2B-s32B-b82K") -> None:
        super().__init__()
        self.model_name = model_name
        logger.info(self.model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def get_similarity(self, file: bytes, prompt: str) -> float:
        image = Image.open(BytesIO(file))
        inputs = self.processor(
            text=prompt, images=image, return_tensors="pt", padding=True
        )
        inputs["input_ids"] = inputs["input_ids"].to(self.device)
        inputs["attention_mask"] = inputs["attention_mask"].to(self.device)
        inputs["pixel_values"] = inputs["pixel_values"].to(self.device)
        outputs = self.model(**inputs)
        score = outputs.logits_per_image.sum().tolist() / 100
        return score

    def get_metadata(self) -> dict:
        return {"model": self.model_name}


class NSFWChecker(Module):
    def __init__(self) -> None:
        super().__init__()
        self.model_name = "Falconsai/nsfw_image_detection"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.classifier = pipeline(
            "image-classification",
            model="Falconsai/nsfw_image_detection",
            device=self.device,
        )

    def check_nsfw(self, file: bytes) -> bool:
        image = Image.open(BytesIO(file))
        for c in self.classifier(image):
            if c["label"] == "nsfw" and c["score"] > 0.8:
                return True
        return False


if __name__ == "__main__":
    import httpx

    resp = httpx.get("http://images.cocodataset.org/val2017/000000039769.jpg")
    image = resp.content
    c = CLIP()
    score_cat = c.get_similarity(file=image, prompt="cat")
    score_dog = c.get_similarity(file=image, prompt="dog")
    print(score_cat, score_dog)

    nc = NSFWChecker()
    is_nsfw = nc.check_nsfw(image)
    print(is_nsfw)
