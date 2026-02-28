.PHONY: dev-backend dev-frontend dev build test docker-up docker-down clean install

# Backend development server
dev-backend:
	cd backend && uvicorn main:app --reload --port 8000

# Frontend development server
dev-frontend:
	cd frontend && npm run dev

# Run both concurrently (requires 'concurrently' or tmux)
dev:
	@echo "Starting backend and frontend..."
	@make -j2 dev-backend dev-frontend

# Build frontend
build:
	cd frontend && npm run build

# Install all dependencies
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# Run tests
test:
	cd backend && pytest tests/ -v

# Docker operations
docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

# Clean generated files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/chroma_data
	rm -rf frontend/dist
	rm -rf frontend/node_modules
