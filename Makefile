install:
	poetry install

start:
	poetry run flask --app example --debug run

package-install:
	python3 -m pip install --user --force-reinstall dist/*.whl

start-gunicorn:
	poetry run gunicorn --workers=5 --bind=127.0.0.1:5000 example:app
