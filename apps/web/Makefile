include .env.local

ARTIFACT_REGISTRY=$(REGION)-docker.pkg.dev/$(PROJECT_ID)/ejan-minimum
IMAGE_PATH=${ARTIFACT_REGISTRY}/web:latest
SERVICE_ACCOUNT_EMAIL="ejan-minimum-dev-sa@$(PROJECT_ID).iam.gserviceaccount.com"
ENV_VARS="NODE_ENV=production,PROJECT_ID=$(PROJECT_ID),REGION=$(REGION),NEXT_PUBLIC_API_URL=$(NEXT_PUBLIC_API_URL),NEXT_PUBLIC_STORAGE_URL=$(NEXT_PUBLIC_STORAGE_URL)"

.PHONY: build
build:
	docker build --platform linux/amd64 -t ${IMAGE_PATH} --build-arg NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL}" --build-arg NEXT_PUBLIC_STORAGE_URL="${NEXT_PUBLIC_STORAGE_URL}" .

.PHONY: push
push:
	docker push ${IMAGE_PATH}

.PHONY: deploy
deploy:
	gcloud run deploy ejan-web \
    --image ${IMAGE_PATH} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 3000 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 100 \
    --set-env-vars=${ENV_VARS}
