
install:
	pip install -r requirements.txt

test:
	python manage.py test

server:
	python manage.py run

run: test server
