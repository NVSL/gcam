default: build test

.PHONY: build
build:
	if [ "$$USE_VENV." = "yes." ]; then\
	  echo python ./setup.py build develop;\
	  python ./setup.py build develop;\
	else\
	  echo sudo python ./setup.py build develop;\
	  sudo python ./setup.py build develop;\
	fi

test:
