.EXPORT_ALL_VARIABLES:

TMP_CONFIG=/tmp/mkdocs.yml
CUSTOM_DIR=$(shell realpath overrides)

all:
	@echo "Usage: "
	@echo "  make serve"
	@echo "  make build"

build: blend-yml
	mkdocs build -f $(TMP_CONFIG)

serve: blend-yml
	mkdocs serve -f $(TMP_CONFIG)

gh-deploy: blend-yml
	mkdocs gh-deploy --force -f $(TMP_CONFIG)

blend-yml:
	echo "docs_dir: $(realpath docs)" > $(TMP_CONFIG)
	cat mkdocs.yml >> $(TMP_CONFIG)
ifdef G_PROPERTY
	@echo "\e[33mGoogle Analytics enabled.\e[0m"
	@echo "G_PROPERTY=$(G_PROPERTY)"
	cat mkdocs-extra.yml >> $(TMP_CONFIG)
else
	@echo "\e[33mGoogle Analytics disabled.\e[0m"
endif