say_hello:
	echo "hello"

up:
	docker-compose -f docker-compose.yaml up -d

down:
	docker-compose -f docker-compose.yaml down -v --remove-orphans

worker:
	celery -A app.tasks.celery:celery worker -l info

flower:
	celery -A app.tasks.celery:celery flower --port=5555

make migrations:
	alembic revision --autogenerate -m "DataBase initial" && alembic upgrade head