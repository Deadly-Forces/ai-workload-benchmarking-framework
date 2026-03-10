"""Script to download the required open source LLM from HuggingFace to the local models folder."""

import sys
from pathlib import Path

# Setup project root explicitly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# pylint: disable=wrong-import-position
from app.config.constants import GENAI_MODELS
from app.features.genai.model_utils import download_model

# pylint: enable=wrong-import-position


def download_genai_models():
    """Download the generated OpenVINO INT4 model from HuggingFace to the configured path."""
    print("=== Downloading OpenVINO GenAI Models ===")

    for model_key, model_info in GENAI_MODELS.items():
        hf_repo = model_info.get("hf_repo")
        if not hf_repo:
            continue

        print(f"\n> Downloading '{model_info['name']}' from '{hf_repo}'...")
        print("This may take a few minutes as it downloads ~800MB - 2GB of weights.")

        try:
            downloaded_path = download_model(model_key)
            print(f"\n✓ Successfully downloaded model to {downloaded_path}")
        except Exception as e:  # pylint: disable=broad-except
            print(f"\n! Error downloading model: {e}")
            print("Please ensure your internet connection is active.")


if __name__ == "__main__":
    download_genai_models()
