default: build test

.PHONY: build
build:
	@if [ "$$USE_VENV." = "yes." ]; then\
	  echo python ./setup.py build develop;\
	  python ./setup.py build develop;\
	else\
	  echo python ./setup.py build;\
	  python ./setup.py build;\
	fi

test:
