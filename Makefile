# Makefile for convenient Django project commands

# Django manage.py helper
DJANGO=python manage.py

.PHONY: help run migrate makemigrations create superuser test shell collectstatic

help:
	@echo "Available commands:"
	@echo "  run            - start development server (default 8000)"
	@echo "  mgr            - apply database migrations"
	@echo "  mkmgr          - create new migrations for apps"
	@echo "  su             - create an admin user interactively"
	@echo "  test           - run test suite"
	@echo "  shell          - open Django shell"
	@echo "  collectstatic  - collect static files"

run:
	$(DJANGO) runserver

mgr:
	$(DJANGO) migrate

mkmgr:
	$(DJANGO) makemigrations

su:
	$(DJANGO) createsuperuser

test:
	$(DJANGO) test

shell:
	$(DJANGO) shell

collectstatic:
	$(DJANGO) collectstatic --noinput
