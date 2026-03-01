# -----------------------------------------------------------------------------
# Django Makefile
# -----------------------------------------------------------------------------
# Usage:
#   make help
#   make run
#   make run PORT=9000
#   make startapp APP=users
#   make sqlmigrate APP=users NAME=0001
# -----------------------------------------------------------------------------

# Django manage.py helper
DJANGO = python manage.py

# Default variables (can be overridden)
PORT ?= 8000
APP ?=
NAME ?=

# -----------------------------------------------------------------------------
# PHONY TARGETS
# -----------------------------------------------------------------------------

.PHONY: help \
	run runserver \
	migrate mgr mkmgr showmigrations sqlmigrate flush seed \
	su createsuperuser shell dbshell \
	test check \
	collectstatic clearsessions \
	startapp startproject \
	loaddata dumpdata \
	makemessages compilemessages

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------

help:
	@echo ""
	@echo "Django Development Commands"
	@echo "------------------------------------------------------------------"
	@echo " run               Start development server (PORT=8000)"
	@echo ""
	@echo " migrate | mgr     Apply pending database migrations"
	@echo " mkmgr             Create migrations from model changes"
	@echo " showmigrations    Show migration status"
	@echo " sqlmigrate        Show SQL for migration (APP=x NAME=0001)"
	@echo " flush             Remove all database data (keeps schema)"
	@echo " seed              Seed the database with dummy users and 1000 candidates"
	@echo ""
	@echo " su                Create admin superuser"
	@echo " shell             Open Django shell"
	@echo " dbshell           Open database shell"
	@echo ""
	@echo " test              Run Django tests"
	@echo " check             Run Django system checks"
	@echo ""
	@echo " collectstatic     Collect static files"
	@echo " clearsessions     Remove expired sessions"
	@echo ""
	@echo " startapp          Create new app (APP=name)"
	@echo " startproject      Create new project (NAME=name)"
	@echo ""
	@echo " loaddata          Load fixtures (NAME=file)"
	@echo " dumpdata          Export database to dump.json"
	@echo ""
	@echo " makemessages      Extract translation strings"
	@echo " compilemessages   Compile translation files"
	@echo ""

# -----------------------------------------------------------------------------
# Server
# -----------------------------------------------------------------------------

run runserver:
	$(DJANGO) runserver 0.0.0.0:$(PORT)

# -----------------------------------------------------------------------------
# Migrations
# -----------------------------------------------------------------------------

migrate mgr:
	$(DJANGO) migrate

mkmgr:
	$(DJANGO) makemigrations

showmigrations:
	$(DJANGO) showmigrations

sqlmigrate:
	$(DJANGO) sqlmigrate $(APP) $(NAME)

flush:
	$(DJANGO) flush --noinput

seed:
	$(DJANGO) seed --candidates 1000

# -----------------------------------------------------------------------------
# Users / Shell
# -----------------------------------------------------------------------------

su createsuperuser:
	$(DJANGO) createsuperuser

shell:
	$(DJANGO) shell

dbshell:
	$(DJANGO) dbshell

# -----------------------------------------------------------------------------
# Testing & Checks
# -----------------------------------------------------------------------------

test:
	$(DJANGO) test

check:
	$(DJANGO) check

# -----------------------------------------------------------------------------
# Static & Sessions
# -----------------------------------------------------------------------------

collectstatic:
	$(DJANGO) collectstatic --noinput

clearsessions:
	$(DJANGO) clearsessions

# -----------------------------------------------------------------------------
# Project Scaffolding
# -----------------------------------------------------------------------------

startapp:
	@if [ -z "$(APP)" ]; then \
		echo "ERROR: Provide APP name → make startapp APP=myapp"; \
		exit 1; \
	fi
	$(DJANGO) startapp $(APP)

startproject:
	@if [ -z "$(NAME)" ]; then \
		echo "ERROR: Provide NAME → make startproject NAME=myproj"; \
		exit 1; \
	fi
	$(DJANGO) startproject $(NAME)

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

loaddata:
	@if [ -z "$(NAME)" ]; then \
		echo "ERROR: Provide fixture name → make loaddata NAME=data.json"; \
		exit 1; \
	fi
	$(DJANGO) loaddata $(NAME)

dumpdata:
	$(DJANGO) dumpdata > dump.json

# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------

makemessages:
	$(DJANGO) makemessages -a

compilemessages:
	$(DJANGO) compilemessages