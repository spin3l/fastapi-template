.PHONY: generate test-template hooks clean

# Generate a new project next to this repo (interactive prompts).
generate:
	uv run cookiecutter . --output-dir ..

# Render the template with several answer sets and run each project's `make check`.
test-template:
	./scripts/test_template.sh

hooks:
	uv run pre-commit install

clean:
	rm -rf .generated
