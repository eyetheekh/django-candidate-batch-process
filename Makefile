# Makefile for convenient Django project commands

# Django manage.py helper
DJANGO=python manage.py

.PHONY: help run migrate makemigrations create superuser test shell collectstatic startapp startproject

help:
	@echo "Available commands:"
	@echo "  run            - start development server (default 8000)"
	@echo "  mgr            - apply database migrations"
	@echo "  mkmgr          - create new migrations for apps"
	@echo "  su             - create an admin user interactively"
	@echo "  test           - run test suite"
	@echo "  shell          - open Django shell"
	@echo "  collectstatic  - collect static files"
	@echo "  startapp       - create a new Django app (usage: make startapp APP=name)"
	@echo "  startproject   - create a new Django project (usage: make startproject NAME=name)"

su:
	$(DJANGO) createsuperuser

test:
	$(DJANGO) test

shell:
	$(DJANGO) shell

collectstatic:
	$(DJANGO) collectstatic --noinput

startapp:
	$(DJANGO) startapp $(APP)

startproject:
	$(DJANGO) startproject $(NAME)
