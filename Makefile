include ../Gadgetron/dev.make

.PHONY: test
test:
	true

.PHONY:clean
clean:
	rm -rf gcam.egg-info || sudo rm -rf gcam.egg-info
	rm -rf build || sudo rm -rf build
