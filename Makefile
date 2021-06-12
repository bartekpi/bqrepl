install_dev:
	python -m pip install --editable .

clean:
	rm -fr dist
	rm -fr build
	rm -fr *.egg-info

build:
	python -m build

deploy:
	twine upload dist/*
