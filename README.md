# Fruteria-Eli
DJango website, API integration for payments

# Local Testing
## 1. Source 
Python env

## 2.
python3 run migrations

## 3.
python3 run server

# Deployment Strategy:
## 1. Build
docker buildx build --platform linux/amd64 -t fruteriaelireg.azurecr.io/fruteria-eli:latest .

## 2. Push
docker push fruteriaelireg.azurecr.io/fruteria-eli:latest

## 3. Restart
az webapp restart --name fruteria-eli-app --resource-group Fruteria-Eli