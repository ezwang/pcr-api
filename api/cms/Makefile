.PHONY: server
server:
	@python ../manage.py runserver

.PHONY: static
static:
	@coffee -o static/js -c static/coffee
	@lessc static/less/* > static/css/vendor.css

