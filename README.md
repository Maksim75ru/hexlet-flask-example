# hexlet-flask-example

### Учебный проект по фреймворку Flask

make install:
	poetry install

make start:
	poetry run flask --app example --debug run

make package-install:
	python3 -m pip install --user --force-reinstall dist/*.whl