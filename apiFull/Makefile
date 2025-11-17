.PHONY: help install run test clean docker-build docker-up docker-down

help:
	@echo "Comandos disponibles:"
	@echo "  make install       - Instalar dependencias"
	@echo "  make run          - Ejecutar aplicación"
	@echo "  make test         - Ejecutar tests"
	@echo "  make clean        - Limpiar archivos temporales"
	@echo "  make docker-build - Construir imagen Docker"
	@echo "  make docker-up    - Iniciar con Docker Compose"
	@echo "  make docker-down  - Detener Docker Compose"

install:
	pip install -r requirements.txt

run:
	python app.py

test:
	pytest --cov=app tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

logs:
	docker-compose logs -f api

init-db:
	sqlite3 database.db < schema_sqlite.sql