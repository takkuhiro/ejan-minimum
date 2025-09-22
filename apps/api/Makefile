include .env

ARTIFACT_REGISTRY=$(REGION)-docker.pkg.dev/$(PROJECT_ID)/ejan-minimum
IMAGE_PATH=${ARTIFACT_REGISTRY}/api:latest
SERVICE_ACCOUNT_EMAIL="ejan-minimum-dev-sa@$(PROJECT_ID).iam.gserviceaccount.com"
ENV_VARS="GOOGLE_API_KEY=$(GOOGLE_API_KEY),GOOGLE_CLOUD_PROJECT=$(PROJECT_ID),STORAGE_BUCKET=$(STORAGE_BUCKET),REGION=$(REGION),ENV=production,CORS_ORIGINS=$(CORS_ORIGINS),CLOUD_FUNCTION_URL=$(CLOUD_FUNCTION_URL)"

.PHONY: vet
vet:
	uv run ruff format .
	uv run ruff check . --fix
	uv run mypy .

.PHONY: build
build:
	docker build --platform linux/amd64 -t ${IMAGE_PATH} .

.PHONY: push
push:
	docker push ${IMAGE_PATH}

.PHONY: deploy
deploy:
	gcloud run deploy ejan-api \
    --image ${IMAGE_PATH} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 100 \
    --service-account ${SERVICE_ACCOUNT_EMAIL} \
    --set-env-vars=${ENV_VARS}
