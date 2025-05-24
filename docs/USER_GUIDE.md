# Stunning Modeling Studio - User Guide

## Introduction

Welcome to the Stunning Modeling Studio system! This comprehensive guide will walk you through the installation, setup, and usage of this powerful local-first AI modeling system. Stunning allows you to create, manage, and customize AI-generated models with layered styling capabilities, making it perfect for design professionals, creative agencies, and content creators.

## Table of Contents

1. [Installation & Prerequisites](#installation--prerequisites)
2. [Setting Up the Environment](#setting-up-the-environment)
3. [Running the Application](#running-the-application)
4. [Using the Stunning Modeling Studio](#using-the-stunning-modeling-studio)
   - [Client Management](#client-management)
   - [Model Creation](#model-creation)
   - [Styling and Editing](#styling-and-editing)
   - [Lookbooks and History](#lookbooks-and-history)
   - [Template Management](#template-management)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Configuration](#advanced-configuration)

## Installation & Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)
- **CPU**: Minimum 4 cores, 8+ cores recommended
- **RAM**: Minimum 16GB, 32GB+ recommended
- **Storage**: 20GB free space for application, 50GB+ recommended for model storage
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for optimal performance)
  - CUDA 11.7+ and cuDNN required for GPU acceleration
  - Apple Silicon Macs can use MPS acceleration

### Prerequisites

Before installing Stunning, ensure you have the following prerequisites installed:

1. **Python Environment**:
   - Python 3.9+ is required
   - We recommend using a virtual environment manager like Conda or venv

   ```bash
   # Install Python 3.9+ if not already installed
   # For Ubuntu
   sudo apt update
   sudo apt install python3.9 python3.9-dev python3.9-venv
   
   # For macOS (using Homebrew)
   brew install python@3.9
   
   # For Windows
   # Download and install from python.org
   ```

2. **Node.js**:
   - Node.js 16.x or later is required
   - npm 7.x or later is required

   ```bash
   # Install Node.js and npm
   # For Ubuntu
   curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
   sudo apt install -y nodejs
   
   # For macOS
   brew install node@16
   
   # For Windows
   # Download and install from nodejs.org
   ```

3. **GPU Drivers** (for NVIDIA GPUs):
   - Install the latest NVIDIA drivers
   - Install CUDA Toolkit 11.7+ and cuDNN

   ```bash
   # For Ubuntu
   sudo apt install nvidia-driver-XXX
   # Download and install CUDA from NVIDIA website
   
   # For Windows/macOS
   # Download and install from NVIDIA website
   ```

## Setting Up the Environment

### Clone the Repository

```bash
git clone https://github.com/yourusername/stunning.git
cd stunning
```

### Backend Setup

1. Create and activate a Python virtual environment:

```bash
# Using venv
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Or using Conda
conda create -n stunning python=3.9
conda activate stunning
```

2. Install backend dependencies:

```bash
cd src/backend
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
# Create a .env file in the backend directory
touch .env

# Add the following variables to the .env file
DATABASE_URL=sqlite:///./stunning.db
SECRET_KEY=your_secret_key_here
MODEL_STORAGE_PATH=./models
UPLOAD_FOLDER=./uploads
```

### Frontend Setup

1. Install frontend dependencies:

```bash
cd src/frontend
npm install
```

2. Configure environment variables:

```bash
# Create a .env.local file in the frontend directory
touch .env.local

# Add the following variables to the .env.local file
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Using Docker (Recommended)

The easiest way to run Stunning is using Docker Compose:

```bash
# From the project root
docker-compose up
```

This will start both the backend and frontend services, and the application will be available at http://localhost:3000.

### Manual Startup

If you prefer to run the services manually:

1. Start the backend server:

```bash
# From the project root
cd src/backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

2. In a separate terminal, start the frontend development server:

```bash
# From the project root
cd src/frontend
npm run dev
```

3. Access the application at http://localhost:3000

## Using the Stunning Modeling Studio

### Client Management

The first step in using Stunning is to create and manage clients. Each client can have multiple models and lookbooks.

#### Creating a New Client

1. From the home screen, click the "+ NEW" button in the top-right corner.
2. Fill in the client details:
   - Name: The client's name
   - Description: A brief description of the client
   - Theme Settings: Customize the UI theme for this client (optional)
3. Click "Create Client" to save.

![Client Creation Form](../screenshots/client_creation.png)

#### Managing Clients

- To edit a client, select the client from the home screen and click "Settings" > "Edit Client".
- To delete a client, go to "Settings" > "Delete Client". Note that this will also delete all associated models and history.

### Model Creation

Once you have created a client, you can create models for them.

#### Creating a Base Model

1. Select a client from the home screen.
2. Click on the "Models" tab.
3. Click the "+ New Model" button.
4. Fill in the model details:
   - Name: A name for the model
   - Reference Images: Upload 3-5 high-quality reference images
   - Description: Optional notes about the model
5. Click "Create Model" to process the images and create the base embedding.

The system will process the reference images and create a base embedding using Stable Diffusion. This may take a few minutes depending on your hardware.

![Model Creation Process](../screenshots/model_creation.png)

### Styling and Editing

The Studio dashboard is where you'll spend most of your time styling and editing models.

#### Applying Styling Layers

1. Select a client and then a model from the sidebar.
2. Use the dropdown menus to select:
   - Hair Style: Choose from predefined hair styles or create a custom one
   - Outfit: Select clothing options
   - Scene/Background: Choose the environment
3. Click "Generate" to apply the styling layers to the base model.

The system will combine the base model with the selected styling layers to generate a preview image.

#### Using Prompt-Based Editing

For more fine-grained control:

1. Enter a text prompt in the prompt field below the preview.
   - Example: "Add a blue scarf and make the lighting warmer"
2. Click "Generate" to apply the prompt-based edits.

#### Inpainting and Targeted Edits

For targeted modifications to specific areas:

1. Click the "Inpaint" button below the preview.
2. Use the brush tool to mask the area you want to modify.
3. Enter a prompt describing the desired change.
4. Click "Apply" to make the targeted edit.

![Studio Dashboard](../screenshots/studio_dashboard.png)

### Lookbooks and History

The Lookbook feature allows you to browse and restore previous versions of your models.

#### Viewing History

1. Click on the "Lookbook" tab.
2. Browse through the history of generated images.
3. Use the filter dropdown to filter by model.

#### Restoring Previous Versions

1. Find the image you want to restore in the Lookbook.
2. Click the "Restore" button below the image.
3. The image and its settings will be loaded into the Studio for further editing.

#### Creating a Lookbook Collection

1. Select multiple images by checking the boxes in the top-right corner of each image.
2. Click "Create Collection" at the top of the page.
3. Enter a name and description for the collection.
4. Click "Save" to create the collection.

![Lookbook Interface](../screenshots/lookbook.png)

### Template Management

Templates allow you to save and reuse styling configurations.

#### Managing Templates

1. Click on the "Templates" tab.
2. Select the template type (Hair, Outfit, or Background).
3. Browse existing templates or create new ones.

#### Creating a New Template

1. Click the "+ Add New" button.
2. Fill in the template details:
   - Name: A name for the template
   - Type: Select the template type
   - Prompt: The text prompt that defines this template
   - Negative Prompt: Optional text to exclude from generation
   - Strength: Adjust the influence of this template
   - Reference: Optionally upload a reference image
3. Click "Save" to create the template.

![Template Manager](../screenshots/template_manager.png)

## Troubleshooting

### Common Issues

#### Backend Won't Start

- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify that the .env file exists with the correct variables
- Ensure the database path is writable
- Check for port conflicts on 8000

#### Frontend Won't Start

- Verify that all dependencies are installed: `npm install`
- Check that the .env.local file exists with the correct API URL
- Ensure Node.js version is 16.x or later

#### Slow Image Generation

- Check GPU utilization and CUDA installation
- Reduce the resolution in Settings > Performance
- Close other GPU-intensive applications

#### "Out of Memory" Errors

- Reduce the model size in Settings > Performance
- Increase your system's swap space
- Upgrade your RAM or GPU

### Getting Help

If you encounter issues not covered here:

1. Check the logs:
   - Backend logs: `docker-compose logs backend`
   - Frontend logs: `docker-compose logs frontend`
2. Visit our GitHub repository to file an issue
3. Check the FAQ section on our website

## Advanced Configuration

### Custom Model Integration

Stunning supports integration with custom Stable Diffusion models:

1. Place your custom model files in the `models` directory.
2. Edit the `config.yaml` file to include your model:

```yaml
models:
  - name: "My Custom Model"
    path: "./models/my_custom_model.safetensors"
    type: "stable-diffusion-xl"
```

### Performance Tuning

Adjust performance settings in the `config.yaml` file:

```yaml
performance:
  precision: "fp16"  # Options: fp32, fp16, bf16
  batch_size: 1
  resolution: 768
  optimization: "xformers"  # Options: xformers, sdpa, none
```

### Security Configuration

Enhance security settings in the `config.yaml` file:

```yaml
security:
  jwt_expiration: 86400  # Token expiration in seconds
  password_min_length: 12
  require_2fa: false
  cors_origins:
    - "http://localhost:3000"
    - "https://yourdomain.com"
```

### Backup and Restore

To back up your data:

```bash
# From the project root
./scripts/backup.sh
```

This will create a backup of your database and generated images in the `backups` directory.

To restore from a backup:

```bash
# From the project root
./scripts/restore.sh backups/backup_2023-05-24.zip
```
