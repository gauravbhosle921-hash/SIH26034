import io
import re
from PIL import Image
import cv2
import numpy as np
import pytesseract
from pytesseract import Output

class OCRService:
    def preprocess(self, raw: bytes):
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        img.thumbnail((2400, 2400))
        arr = np.array(img)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        gray = cv2.fastNlMeansDenoising(gray, None, 7, 7, 21)
        gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
        sharp = cv2.GaussianBlur(gray, (0, 0), 1.0)
        sharp = cv2.addWeighted(gray, 1.5, sharp, -0.5, 0)
        return sharp

    def run(self, raw: bytes):
        img = self.preprocess(raw)
        config = "--oem 3 --psm 11"
        data = pytesseract.image_to_data(img, config=config, output_type=Output.DICT, lang="eng")
        words = []
        for i, txt in enumerate(data["text"]):
            txt = re.sub(r"\s+", " ", txt or "").strip()
            try: conf = float(data["conf"][i])
            except Exception: conf = -1
            if txt and conf >= 0:
                words.append({"text": txt, "confidence": round(conf, 1), "x": int(data["left"][i]), "y": int(data["top"][i]), "w": int(data["width"][i]), "h": int(data["height"][i])})
        full_text = " ".join(w["text"] for w in words)
        return {"text": full_text, "words": words, "image_width": int(img.shape[1]), "image_height": int(img.shape[0])}
