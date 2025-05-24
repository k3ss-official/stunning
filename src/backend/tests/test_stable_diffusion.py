import pytest
from unittest.mock import patch, MagicMock
import os
import torch
from PIL import Image

from ai_models.stable_diffusion import StableDiffusionModel

@pytest.fixture
def sd_model():
    # Create a test instance with CPU device to avoid GPU requirements in CI
    model = StableDiffusionModel(device="cpu")
    
    # Create test directories if they don't exist
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("generated", exist_ok=True)
    
    return model

@patch("ai_models.stable_diffusion.StableDiffusionPipeline")
def test_generate_image(mock_pipeline, sd_model):
    # Mock the pipeline and its output
    mock_instance = MagicMock()
    mock_pipeline.from_pretrained.return_value = mock_instance
    
    # Create a mock image
    mock_image = MagicMock(spec=Image.Image)
    mock_instance.return_value = MagicMock(images=[mock_image])
    
    # Test generate_image method
    result_image, output_path = sd_model.generate_image(
        prompt="test prompt",
        negative_prompt="test negative",
        output_path="generated/test.png"
    )
    
    # Verify the pipeline was called with correct parameters
    mock_instance.assert_called_once()
    call_kwargs = mock_instance.call_args.kwargs
    assert call_kwargs["prompt"] == "test prompt"
    assert call_kwargs["negative_prompt"] == "test negative"
    
    # Verify the result
    assert result_image == mock_image
    assert output_path == "generated/test.png"

@patch("ai_models.stable_diffusion.StableDiffusionInpaintPipeline")
def test_inpaint_image(mock_pipeline, sd_model):
    # Mock the pipeline and its output
    mock_instance = MagicMock()
    mock_pipeline.from_pretrained.return_value = mock_instance
    
    # Create mock images
    mock_image = MagicMock(spec=Image.Image)
    mock_image.convert.return_value = mock_image
    
    mock_mask = MagicMock(spec=Image.Image)
    mock_mask.convert.return_value = mock_mask
    
    mock_result = MagicMock(spec=Image.Image)
    mock_instance.return_value = MagicMock(images=[mock_result])
    
    # Test inpaint_image method
    result_image, output_path = sd_model.inpaint_image(
        image=mock_image,
        mask_image=mock_mask,
        prompt="test inpaint",
        output_path="generated/inpaint_test.png"
    )
    
    # Verify the pipeline was called with correct parameters
    mock_instance.assert_called_once()
    call_kwargs = mock_instance.call_args.kwargs
    assert call_kwargs["prompt"] == "test inpaint"
    assert call_kwargs["image"] == mock_image
    assert call_kwargs["mask_image"] == mock_mask
    
    # Verify the result
    assert result_image == mock_result
    assert output_path == "generated/inpaint_test.png"

def test_apply_styling_layers(sd_model):
    # Mock the generate_image method
    sd_model.generate_image = MagicMock(return_value=(MagicMock(), "generated/styled_test.png"))
    
    # Test apply_styling_layers method
    hair_layer = {"prompt": "long hair", "negative_prompt": "bald"}
    outfit_layer = {"prompt": "blue dress", "negative_prompt": "naked"}
    scene_layer = {"prompt": "beach sunset", "negative_prompt": "indoor"}
    
    _, output_path = sd_model.apply_styling_layers(
        base_model_path="test_embedding.pt",
        hair_layer=hair_layer,
        outfit_layer=outfit_layer,
        scene_layer=scene_layer,
        prompt="beautiful woman",
        negative_prompt="ugly",
        output_path="generated/styled_test.png"
    )
    
    # Verify generate_image was called with combined prompts
    sd_model.generate_image.assert_called_once()
    call_args = sd_model.generate_image.call_args
    assert "beautiful woman" in call_args[1]["prompt"]
    assert "long hair" in call_args[1]["prompt"]
    assert "blue dress" in call_args[1]["prompt"]
    assert "beach sunset" in call_args[1]["prompt"]
    assert "ugly" in call_args[1]["negative_prompt"]
    assert "bald" in call_args[1]["negative_prompt"]
    assert "naked" in call_args[1]["negative_prompt"]
    assert "indoor" in call_args[1]["negative_prompt"]
    
    # Verify the output path
    assert output_path == "generated/styled_test.png"

def test_create_embedding(sd_model):
    # Test create_embedding method
    reference_images = ["test1.jpg", "test2.jpg"]
    output_path = sd_model.create_embedding(
        reference_images=reference_images,
        output_path="generated/test_embedding.pt"
    )
    
    # Verify the output path
    assert output_path == "generated/test_embedding.pt"
    
    # Verify the file was created (in this case, it's a simulated file)
    assert os.path.exists(output_path)
