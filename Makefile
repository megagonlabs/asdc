
all: lint_markdown lint_python check_data test

SHELL=/bin/bash

include mks/path.mk
include mks/lint.mk
include mks/check_data.mk
include mks/generate_main_scud.mk


.PHONY: all setup setup_npm \
    lint_markdown setup_python \
    lint_python pyright black flake8 isort yamllint jsonlint\
    check_data check_format \
    update_original_scud_text \
    generate_main_scud \
    generate_main_split \

.DELETE_ON_ERROR:
