.PHONY: clean test

clean:
	rm -rf build dist *.egg-info

test:
	PYTHONPATH=. deptest -s

publish:
	python setup.py sdist bdist_wheel upload
