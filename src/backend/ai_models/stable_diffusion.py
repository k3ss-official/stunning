import os
import torch
from diffusers import StableDiffusionPipeline, StableDiffusionInpaintPipeline
from diffusers import DDIMScheduler, EulerDiscreteScheduler, DPMSolverMultistepScheduler
from PIL import Image
import uuid
from typing import Dict, Any, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)

class StableDiffusionModel:
    """
    Abstraction layer for Stable Diffusion models.
    Handles text-to-image and image-to-image generation with various models.
    """
    
    def __init__(self, model_path: str = "runwayml/stable-diffusion-v1-5", device: str = None):
        """
        Initialize the Stable Diffusion model.
        
        Args:
            model_path: Path to the model or model identifier from huggingface.co/models
            device: Device to use (cuda, cpu, mps). If None, will use CUDA if available.
        """
        self.model_path = model_path
        
        # Determine device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            if self.device == "cpu" and torch.backends.mps.is_available():
                self.device = "mps"  # Use MPS for Apple Silicon
        else:
            self.device = device
            
        logger.info(f"Using device: {self.device}")
        
        # Initialize pipelines to None (will be loaded on demand)
        self.txt2img_pipeline = None
        self.inpaint_pipeline = None
        
        # Create output directories if they don't exist
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("generated", exist_ok=True)
        
    def _load_txt2img_pipeline(self):
        """Load the text-to-image pipeline if not already loaded."""
        if self.txt2img_pipeline is None:
            logger.info(f"Loading text-to-image pipeline from {self.model_path}")
            
            # Load the pipeline with a scheduler that supports img2img
            scheduler = DDIMScheduler.from_pretrained(
                self.model_path, subfolder="scheduler"
            )
            
            self.txt2img_pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_path,
                scheduler=scheduler,
                safety_checker=None,  # Disable safety checker for performance
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            self.txt2img_pipeline.to(self.device)
            
            # Enable memory efficient attention if using CUDA
            if self.device == "cuda":
                self.txt2img_pipeline.enable_xformers_memory_efficient_attention()
                
            logger.info("Text-to-image pipeline loaded successfully")
    
    def _load_inpaint_pipeline(self):
        """Load the inpainting pipeline if not already loaded."""
        if self.inpaint_pipeline is None:
            logger.info(f"Loading inpainting pipeline from {self.model_path}")
            
            self.inpaint_pipeline = StableDiffusionInpaintPipeline.from_pretrained(
                self.model_path,
                safety_checker=None,  # Disable safety checker for performance
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            self.inpaint_pipeline.to(self.device)
            
            # Enable memory efficient attention if using CUDA
            if self.device == "cuda":
                self.inpaint_pipeline.enable_xformers_memory_efficient_attention()
                
            logger.info("Inpainting pipeline loaded successfully")
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        seed: int = None,
        output_path: str = None,
        **kwargs
    ) -> Tuple[Image.Image, str]:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text prompt for image generation
            negative_prompt: Text prompt for negative conditioning
            width: Output image width
            height: Output image height
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for classifier-free guidance
            seed: Random seed for reproducibility
            output_path: Path to save the generated image
            **kwargs: Additional arguments to pass to the pipeline
            
        Returns:
            Tuple of (PIL Image, output path)
        """
        self._load_txt2img_pipeline()
        
        # Set the seed for reproducibility
        if seed is not None:
            torch.manual_seed(seed)
            torch.cuda.manual_seed(seed) if self.device == "cuda" else None
        
        # Generate the image
        logger.info(f"Generating image with prompt: {prompt}")
        output = self.txt2img_pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            **kwargs
        )
        
        image = output.images[0]
        
        # Save the image if output_path is provided
        if output_path is None:
            output_path = f"generated/{uuid.uuid4()}.png"
        
        image.save(output_path)
        logger.info(f"Image saved to {output_path}")
        
        return image, output_path
    
    def inpaint_image(
        self,
        image: Image.Image,
        mask_image: Image.Image,
        prompt: str,
        negative_prompt: str = None,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        seed: int = None,
        output_path: str = None,
        **kwargs
    ) -> Tuple[Image.Image, str]:
        """
        Inpaint an image based on a mask and prompt.
        
        Args:
            image: Original image to inpaint
            mask_image: Mask image (white areas will be inpainted)
            prompt: Text prompt for inpainting
            negative_prompt: Text prompt for negative conditioning
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for classifier-free guidance
            seed: Random seed for reproducibility
            output_path: Path to save the inpainted image
            **kwargs: Additional arguments to pass to the pipeline
            
        Returns:
            Tuple of (PIL Image, output path)
        """
        self._load_inpaint_pipeline()
        
        # Set the seed for reproducibility
        if seed is not None:
            torch.manual_seed(seed)
            torch.cuda.manual_seed(seed) if self.device == "cuda" else None
        
        # Ensure images are in RGB mode
        image = image.convert("RGB")
        mask_image = mask_image.convert("RGB")
        
        # Generate the inpainted image
        logger.info(f"Inpainting image with prompt: {prompt}")
        output = self.inpaint_pipeline(
            prompt=prompt,
            image=image,
            mask_image=mask_image,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            **kwargs
        )
        
        inpainted_image = output.images[0]
        
        # Save the image if output_path is provided
        if output_path is None:
            output_path = f"generated/{uuid.uuid4()}.png"
        
        inpainted_image.save(output_path)
        logger.info(f"Inpainted image saved to {output_path}")
        
        return inpainted_image, output_path
    
    def create_embedding(
        self,
        reference_images: List[str],
        output_path: str = None,
        num_training_steps: int = 1000,
        learning_rate: float = 5e-6,
        **kwargs
    ) -> str:
        """
        Create a textual inversion embedding from reference images.
        This is a simplified version that would need to be expanded for real use.
        
        Args:
            reference_images: List of paths to reference images
            output_path: Path to save the embedding
            num_training_steps: Number of training steps
            learning_rate: Learning rate for training
            **kwargs: Additional training arguments
            
        Returns:
            Path to the saved embedding
        """
        # In a real implementation, this would use textual inversion or LoRA training
        # For now, we'll just simulate the process
        
        logger.info(f"Creating embedding from {len(reference_images)} reference images")
        
        # Simulate embedding creation
        if output_path is None:
            output_path = f"generated/embedding_{uuid.uuid4()}.pt"
        
        # Create a dummy embedding file
        with open(output_path, "w") as f:
            f.write("This is a simulated embedding file")
        
        logger.info(f"Embedding saved to {output_path}")
        
        return output_path
    
    def apply_styling_layers(
        self,
        base_model_path: str,
        hair_layer: Dict[str, Any] = None,
        outfit_layer: Dict[str, Any] = None,
        scene_layer: Dict[str, Any] = None,
        prompt: str = "",
        negative_prompt: str = "",
        output_path: str = None,
        **kwargs
    ) -> Tuple[Image.Image, str]:
        """
        Apply styling layers to a base model.
        
        Args:
            base_model_path: Path to the base model embedding
            hair_layer: Hair styling layer configuration
            outfit_layer: Outfit styling layer configuration
            scene_layer: Scene styling layer configuration
            prompt: Additional text prompt
            negative_prompt: Negative text prompt
            output_path: Path to save the generated image
            **kwargs: Additional generation parameters
            
        Returns:
            Tuple of (PIL Image, output path)
        """
        self._load_txt2img_pipeline()
        
        # Combine prompts from all layers
        combined_prompt = prompt
        combined_negative_prompt = negative_prompt
        
        if hair_layer:
            combined_prompt += f", {hair_layer.get('prompt', '')}"
            if hair_layer.get('negative_prompt'):
                combined_negative_prompt += f", {hair_layer.get('negative_prompt')}"
        
        if outfit_layer:
            combined_prompt += f", {outfit_layer.get('prompt', '')}"
            if outfit_layer.get('negative_prompt'):
                combined_negative_prompt += f", {outfit_layer.get('negative_prompt')}"
        
        if scene_layer:
            combined_prompt += f", {scene_layer.get('prompt', '')}"
            if scene_layer.get('negative_prompt'):
                combined_negative_prompt += f", {scene_layer.get('negative_prompt')}"
        
        # Generate the image with combined styling
        logger.info(f"Applying styling layers with combined prompt: {combined_prompt}")
        return self.generate_image(
            prompt=combined_prompt,
            negative_prompt=combined_negative_prompt,
            output_path=output_path,
            **kwargs
        )
    
    def unload(self):
        """Unload models from GPU memory."""
        if self.txt2img_pipeline is not None:
            del self.txt2img_pipeline
            self.txt2img_pipeline = None
            
        if self.inpaint_pipeline is not None:
            del self.inpaint_pipeline
            self.inpaint_pipeline = None
            
        if self.device == "cuda":
            torch.cuda.empty_cache()
            
        logger.info("Models unloaded from memory")
