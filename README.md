# hexlet-flask-example

install:
	poetry install

start:
	poetry run flask --app example --debug run

package-install:
	python3 -m pip install --user --force-reinstall dist/*.whl