default: build test

.PHONY: build
build:
	pip install -e .

test:

.PHONY:
clean:
	rm -rf gcam.egg-info || sudo rm -rf gcam.egg-info
	rm -rf build || sudo rm -rf build