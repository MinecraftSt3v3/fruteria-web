# Frutería Elí — Mercado Fresco
A full-stack e-commerce web application for Frutería Elí, a fresh fruit and vegetable market based in Primo Tapia, México. The app allows customers to browse products, manage a cart, checkout with Stripe, and switch between Spanish and English.

## Purpose
Frutería Elí needed an online presence to reach more customers and offer a convenient way to shop for fresh, locally sourced produce. This app brings the market experience online — showcasing daily deals, managing orders, and accepting payments securely.

## Tech Stack
LayerTechnologyBackendPython 3.11, Django 4.2FrontendHTML, CSS, Django TemplatesStatic FilesWhiteNoisePaymentsStripeAuthDjango built-in authDatabaseSQLite (development)ContainerizationDockerContainer RegistryAzure Container Registry (ACR)HostingAzure App Service (Linux)CI/CDGitHub ActionsEnvironment Variablespython-dotenvi18nDjango i18n (Spanish / English)

## GitHub Actions — CI/CD
Every push to main automatically:

- Builds the Docker image for linux/amd64
- Pushes it to Azure Container Registry
- Restarts the Azure App Service

The workflow file lives at .github/workflows/deploy.yml.

Running Locally
Prerequisites

- Python 3.11+
- Docker (optional for local container testing)

1. Clone the repo
- git clone https://github.com/your-username/fruteria-eli.git
cd fruteria-eli
2. Create and activate a virtual environment
- bashpython -m venv myenv
- source myenv/bin/activate        # macOS/Linux

3. Install dependencies
- bashpip install -r requirements.txt

4. Set up environment variables
- Create a .env file in the project root:
- SECRET_KEY=your-secret-key
- DEBUG=True
- STRIPE_PUBLIC_KEY=your-stripe-public-key
- STRIPE_SECRET_KEY=your-stripe-secret-key

5. Run migrations and start the server
- bashpython manage.py migrate
- python manage.py runserver
- Visit http://127.0.0.1:8000

Running with Docker
- bash# Build
- docker buildx build --platform linux/amd64 -t fruteria-eli .

Run
- docker run -p 8000:8000 --env-file .env fruteria-eli
- Visit http://localhost:8000

## Deploying to Azure
Deployment is handled automatically via GitHub Actions on every push to main. To deploy manually:
bash# Build and push to ACR
docker buildx build --platform linux/amd64 -t fruteriaelireg.azurecr.io/fruteria-eli:latest .
docker push fruteriaelireg.azurecr.io/fruteria-eli:latest

Restart App Service
az webapp restart --name fruteria-eli-app --resource-group fruteria-eli-rg

Project Structure
fruteria-eli/
├── fruteria_eli/        # Django project settings, urls, wsgi
├── store/               # Products, cart, orders, views
├── accounts/            # User registration, login, profile
├── templates/           # HTML templates
├── static/              # CSS, JS, images
├── staticfiles/         # Collected static files (generated)
├── .github/workflows/   # GitHub Actions CI/CD
├── Dockerfile
├── requirements.txt
└── manage.py
