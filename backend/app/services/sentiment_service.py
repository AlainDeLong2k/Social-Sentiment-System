from typing import List, Dict, Any
from app.core.config import settings

import torch
import numpy as np
from scipy.special import softmax
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig


class SentimentService:
    """
    A service for loading the sentiment analysis model and performing predictions.
    """

    def __init__(self) -> None:
        """
        Initialize the service by loading the sentiment analysis model and tokenizer.
        """
        # Select device (GPU if available, otherwise CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.device.type == "cuda":
            print(f"GPU found: {torch.cuda.get_device_name(0)}. Loading model onto GPU.")
        else:
            print("GPU not found. Loading model onto CPU.")

        # Load model, tokenizer, and config (for id2label mapping)
        model_name = settings.SENTIMENT_MODEL
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.config = AutoConfig.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(
            self.device
        )
        self.model.eval()  # set model to inference mode
        print("Sentiment model loaded successfully.")

    def _preprocess_text(self, text: str) -> str:
        """
        Replace @user mentions and http links with placeholders.
        """
        if not isinstance(text, str):
            return ""
        new_text = []
        for t in text.split(" "):
            t = "@user" if t.startswith("@") and len(t) > 1 else t
            t = "http" if t.startswith("http") else t
            new_text.append(t)
        return " ".join(new_text)

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predict sentiment for a batch of texts (batch size is assumed to be small).
        """
        # Preprocess all texts
        preprocessed_texts = [self._preprocess_text(text) for text in texts]

        # Keep only non-empty texts and remember their original indices
        non_empty_texts_with_indices = [
            (i, text) for i, text in enumerate(preprocessed_texts) if text.strip()
        ]
        if not non_empty_texts_with_indices:
            return []

        indices, texts_to_predict = zip(*non_empty_texts_with_indices)

        # Tokenize the batch
        encoded_inputs = self.tokenizer(
            list(texts_to_predict),
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(self.device)

        # Run inference
        with torch.no_grad():
            outputs = self.model(**encoded_inputs)
            logits = outputs.logits.detach().cpu().numpy()

        # NEW: Explicitly clear intermediate tensors from VRAM
        del encoded_inputs, outputs  # NEW
        torch.cuda.empty_cache()  # NEW

        # Apply softmax to get probabilities
        probs = softmax(logits, axis=1)

        # Map predictions to labels with highest probability
        predictions = []
        for prob in probs:
            max_idx = int(np.argmax(prob))
            predictions.append(
                {"label": self.config.id2label[max_idx], "score": float(prob[max_idx])}
            )

        # Map predictions back to their original positions
        final_results: List[Dict[str, Any] | None] = [None] * len(texts)
        for original_index, prediction in zip(indices, predictions):
            final_results[original_index] = prediction

        # Replace None results with a default neutral prediction
        default_prediction = {"label": "neutral", "score": 1.0}
        return [res if res is not None else default_prediction for res in final_results]
