# Stunning Modeling Studio

A complete local-first AI modeling studio system for creating, styling, and managing AI-generated models with layered styling capabilities.

## Overview

Stunning is a powerful tool designed for creative professionals who need to generate and manage AI models with consistent styling. The system allows you to:

- Create and manage client profiles
- Generate base models from reference images
- Apply styling layers (hair, outfit, scene)
- Edit models with text prompts and inpainting
- Maintain a history of generated images in lookbooks
- Manage reusable styling templates

## Features

- **Local-First Architecture**: All processing happens on your local machine for privacy and speed
- **Client Management**: Organize models by client with custom theming
- **Base Model Creation**: Generate base embeddings from reference images
- **Layered Styling**: Apply and combine different styling elements
- **Prompt-Based Editing**: Refine models with natural language prompts
- **Inpainting**: Make targeted edits to specific areas
- **History and Lookbooks**: Browse and restore previous versions
- **Template Management**: Save and reuse styling configurations
- **Responsive Design**: Works on desktop and mobile devices
- **Security**: JWT authentication, RBAC, and secure local storage

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Stable Diffusion
- **Frontend**: Next.js, Tailwind CSS, React Query
- **Database**: SQLite/PostgreSQL
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## Quick Start

### Using Docker (Recommended)

The easiest way to get started is with Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/stunning.git
cd stunning

# Start the application
docker-compose up
```

Access the application at http://localhost:3000

### Manual Setup

If you prefer to run the services manually:

1. **Set up the backend**:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd src/backend
pip install -r requirements.txt

# Start the backend server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

2. **Set up the frontend**:

```bash
# Install dependencies
cd src/frontend
npm install

# Start the development server
npm run dev
```

Access the application at http://localhost:3000

## Documentation

For more detailed information, please refer to the following documentation:

- [Architecture Overview](docs/ARCHITECTURE.md): System design and component interactions
- [Entity Relationship Diagram](docs/ERD.png): Database schema visualization
- [Wireframes](docs/WIREFRAMES.md): UI design mockups
- [User Guide](docs/USER_GUIDE.md): Comprehensive usage instructions

## Adding New Clients and Models

### Creating a New Client

1. From the home screen, click the "+ NEW" button
2. Fill in the client details and click "Create Client"

### Creating a New Model

1. Select a client from the home screen
2. Click on the "Models" tab
3. Click the "+ New Model" button
4. Upload reference images and fill in the details
5. Click "Create Model"

## Extending the System

### Adding New Styling Templates

1. Click on the "Templates" tab
2. Select the template type (Hair, Outfit, or Background)
3. Click the "+ Add New" button
4. Fill in the template details and click "Save"

### Integrating Custom AI Models

1. Place your custom model files in the `models` directory
2. Edit the `config.yaml` file to include your model
3. Restart the application

## Development

### Prerequisites

- Python 3.9+
- Node.js 16+
- CUDA 11.7+ and cuDNN (for GPU acceleration)

### Setting Up the Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/stunning.git
cd stunning

# Set up the backend
cd src/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up the frontend
cd ../frontend
npm install
```

### Running Tests

```bash
# Backend tests
cd src/backend
pytest

# Frontend tests
cd src/frontend
npm test
```

## Contributing

We welcome contributions to Stunning! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and commit them: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Stable Diffusion for the underlying AI model
- FastAPI for the backend framework
- Next.js for the frontend framework
- All contributors who have helped shape this project
