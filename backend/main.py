import torch
from transformers import pipeline, Pipeline
from typing import List, Dict, Any


def check_gpu_and_load_model() -> Pipeline | None:
    """
    Checks for GPU availability, prints the status, and loads the sentiment analysis model
    onto the appropriate device (GPU if available, otherwise CPU).
    """
    # 1. Check for GPU
    if torch.cuda.is_available():
        print(f"✅ GPU is available. PyTorch is using: {torch.cuda.get_device_name(0)}")
        device_index = 0  # Use the first available GPU
    else:
        print("⚠️ GPU not found. PyTorch will use CPU. This will be slower.")
        device_index = -1  # Use CPU

    # 2. Load the model using the pipeline
    model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    print(f"\nDownloading and loading model: '{model_name}'...")

    try:
        # device=0 for GPU, device=-1 for CPU
        sentiment_pipeline: Pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            tokenizer=model_name,
            device=device_index,
        )
        print("✅ Model loaded successfully!")
        return sentiment_pipeline
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None


def test_sentiment_prediction(sentiment_pipeline: Pipeline) -> None:
    """
    Tests the sentiment analysis pipeline with sample sentences and prints the results.
    """
    if not sentiment_pipeline:
        print("Pipeline is not available. Skipping test.")
        return

    print("\n--- Testing sentiment prediction ---")

    sample_texts: List[str] = [
        "This is the best movie I have ever seen! Truly amazing.",
        "I'm not sure how I feel about this product, it's just okay.",
        "The customer service was terrible. I am very disappointed.",
        "Python is a versatile programming language.",
        "I can't wait for the weekend!",
    ]

    try:
        results: List[Dict[str, Any]] = sentiment_pipeline(sample_texts)

        for text, result in zip(sample_texts, results):
            # The model labels are 'positive', 'neutral', 'negative'
            label = result.get("label")
            score = result.get("score", 0)
            print(f"\nText: '{text}'")
            print(f"  -> Predicted Sentiment: {label} (Confidence: {score:.2%})")

    except Exception as e:
        print(f"❌ An error occurred during prediction: {e}")


if __name__ == "__main__":
    # Load the model (this will trigger the download on first run)
    pipeline_instance = check_gpu_and_load_model()

    # Test the loaded model
    test_sentiment_prediction(pipeline_instance)
