NAME=lambda-alerting

ifeq (, $(shell which docker-machine))
	export DOCKER_HOST_IP="localhost"
else
	export DOCKER_HOST_IP=$(shell docker-machine ip `docker-machine active`)
endif

test: build/venv
	@( . build/venv/bin/activate;  \
		cd scripts; \
		coverage erase; \
		nosetests --with-xunit --xunit-file=../build/nosetests.xml \
			--with-coverage --cover-package=gdhlib --cover-min-percentage 100 \
			test \
	)

lint: build/venv
	@( . build/venv/bin/activate;  \
		find scripts -not -path 'test/*' -name *.py | xargs pylint --rcfile pylintrc || exit 0 \
	)

build/docker-image:
	@mkdir -p build/
	@docker build -f test/Dockerfile -t $(NAME) .
	@docker inspect -f '{{.Id}}' $(NAME) > build/docker-image

run: build/docker-image
	docker run -d \
		 --name $(NAME) \
		 $(NAME)
	docker exec -i $(NAME) bash  \
		-c 'mkdir -p /git/.aws && cat > /git/.aws/credentials' \
		< ~/.aws/credentials

clean:
	-@vagrant destroy -f
	-@docker kill $(NAME)
	-@docker rm $(NAME)
	rm -Rf build/

build/venv: build/venv/bin/activate

build/venv/bin/activate: requirements.txt test/requirements.txt
	@mkdir -p build
	@test -d build/venv || virtualenv -p /usr/bin/python2.7 --no-site-packages build/venv
	@( . build/venv/bin/activate;  \
		pip install -r scripts/requirements.txt; \
		pip install -r scripts/test/requirements.txt \
	)

.PHONY: test
