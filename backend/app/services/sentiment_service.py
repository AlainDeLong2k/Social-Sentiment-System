import torch
from typing import List, Dict, Any
from transformers import pipeline, Pipeline


class SentimentService:
    """
    A service for loading the sentiment analysis model and performing predictions.
    """

    def __init__(self) -> None:
        """
        Initializes the service by loading the sentiment analysis model onto the appropriate device.
        """
        self.pipeline: Pipeline = self._load_model()

    def _load_model(self) -> Pipeline:
        """
        Checks for GPU availability and loads the sentiment analysis model.
        """
        device_index = 0 if torch.cuda.is_available() else -1
        if device_index == 0:
            print(
                f"GPU found: {torch.cuda.get_device_name(0)}. Loading model onto GPU."
            )
        else:
            print("GPU not found. Loading model onto CPU.")

        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            tokenizer=model_name,
            device=device_index,
            max_length=512,
            padding=True,
            truncation=True,
        )
        print("Sentiment model loaded successfully.")
        return sentiment_pipeline

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocesses a single text by replacing @user mentions and http links.
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
        Takes a batch of texts, preprocesses them, and returns sentiment predictions.
        """
        preprocessed_texts = [self._preprocess_text(text) for text in texts]

        # Filter out any empty strings that might result from preprocessing
        # and keep track of original indices to map results back.
        non_empty_texts_with_indices = [
            (i, text) for i, text in enumerate(preprocessed_texts) if text.strip()
        ]

        if not non_empty_texts_with_indices:
            return []

        indices, texts_to_predict = zip(*non_empty_texts_with_indices)

        predictions = self.pipeline(list(texts_to_predict))

        # Map predictions back to the original batch structure
        final_results: List[Dict[str, Any] | None] = [None] * len(texts)
        for original_index, prediction in zip(indices, predictions):
            final_results[original_index] = prediction

        # Replace None with a default neutral prediction for empty texts
        default_prediction = {"label": "neutral", "score": 1.0}
        return [res if res is not None else default_prediction for res in final_results]
