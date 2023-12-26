# Justfile (Convenience Command Runner) for {{ carnate.project_name }}


# home_dir := env_var('HOME')
local_root := justfile_directory()
invocd_from := invocation_directory()
invoc_is_root := if invocd_from == local_root { "true" } else { "false" }

alias venv := poet-shell

# Default, lists commands.
_default:
        @just --list --unsorted

# initialize project
init:
        which  just  # in case you'e reading ;)
        which pipx
        which poetry
        poetry check
        poetry install
        poetry build

# Open Jupyter Lab in a web browser.
jupyter: _notify_if_not_root
        @echo "Opening Jupyter Lab in a Web Browser\n"
        poetry run jupyter lab

# Enter Poetry Virtual Environment.
poet-shell: _notify_if_not_root
        @echo "Entering Shell running Poetry Virtual Environment\n"
        poetry shell

# Run python file in Poetry venv. (add -m for a module)
py +INP: _notify_if_not_root
        @echo "Running {{INP}} via Python...\n"
        poetry run python3 {{INP}}

# TODO: make this run a script in `.justscripts` See [here](https://just.systems/man/en/chapter_42.html?highlight=bash%20script#safer-bash-shebang-recipes)
# Run Pre-Commit Hook.
hook:
        git hook run pre-commit

# Sync all files in `notebooks/` with Jupytext.
jsync-all: _notify_if_not_root
        #!/bin/bash
        echo "Syncing Jupytext versions of all '.ipynb' notebooks...\n"
        set -xeuo pipefail # euo pipefail: fail flags; x: print commands
        for notebook in notebooks/*.ipynb; do
                poetry run jupytext --set-formats .ipynb,.ju.py:percent "$notebook" # jupytext  % format
                poetry run jupytext --sync "$notebook" # synch .ju.py & .ipynb files
        done


# Sync specified files in `notebooks/` with Jupytext.
jsync +NOTEBOOK: _notify_if_not_root
        @echo "Creating/Syncing Jupytext versions of the following '.ipynb' notebooks {{NOTEBOOK}}...\n"
        poetry run jupytext --set-formats .ipynb,.ju.py:percent notebooks/{{NOTEBOOK}}.ipynb # jupytext  % format
        poetry run jupytext --sync notebooks/{{NOTEBOOK}}.ipynb # synch .ju.py & .ipynb files

# Update Poetry Dependencies.
update:
        @echo "Updating Poetry Virtual Environment...\n"
        poetry update
        poetry check

# Add User dependencies via Poetry.
deps-add +USER_DEPS:
        @echo "Adding the following user dependencies via Poetry: {{USER_DEPS}} ...\n"
        poetry add {{USER_DEPS}}

# Add Developer dependencies via Poetry. (e.g. linters, testers)
deps-add-dev +DEV_DEPS:
        @echo "Adding the following developer dependencies via Poetry: {{DEV_DEPS}} ...\n"
        poetry add --group=dev {{DEV_DEPS}}

# Remove dependencies via Poetry.
deps-remove +DEPS:
        @echo "Removing the following developer dependencies via Poetry: {{DEPS}} ...\n"
        poetry remove {{DEPS}}

# Push Jupyter file changes after jupytext syncing.
push-jup: jsync-all 
        @echo "Auto-Gen File Updates: Committing and Pushing all changes to requirments*.txt & dev_docs/*: {{local_root}}...\n"
        git fetch
        git restore --staged .
        git add notebooks/*
        git commit --message "chore(jupyter): Automated Jupyter updates push.\n\n[note: this is a templated commit]" --no-verify
        git push

# Auto-Gen Files: Add, Commit, and Push all changes.
push-chore: _notify_if_not_root
        @echo "Auto-Gen File Updates: Committing and Pushing all changes to requirments*.txt & dev_docs/*: {{local_root}}...\n"
        git fetch
        git restore --staged .
        git add requirements* dev_docs/*
        git commit --message "chore(auto-gen): requirements files and dev_docs\n\n[note: this is a templated commit]" --no-verify
        git push

# JustFile: Add, Commit, and Push all changes.
push-justfile: _notify_if_not_root
        @echo "JustFile Updates: Committing and Pushing all changes to justfile under root: {{local_root}}...\n"
        git fetch
        git restore --staged .
        git add justfile
        git commit --message "build(auto): updates to justfile (command runner)\n\n[note: this is a templated commit message]" --no-verify
        git push


# Show dependency tree for project.
show-tree:
        @echo "Dependency tree for {{local_root}}\n"
        poetry show --tree --verbose --verbose --verbose

# Show flattened dependency tree for project. (Useful for piping.)
show-list:
        @echo "Dependency list (recursed) for {{local_root}}\n"
        poetry show --verbose --verbose --verbose

# Filtered dependency list results.
show-filter REGEX:
        @echo "Filtered, recursed dependency list for {{local_root}}\n"
        poetry show --verbose --verbose --verbose | grep '{{REGEX}}'

notify_text := "\n-----\nNOTE:\n    You are running this command in:\n"+invocd_from+"\n    But it will be run in:\n" +local_root+".\n-----\n"
_notify_if_not_root:
        @echo '{{ if invoc_is_root == 'true' { "" } else { notify_text } }}'


######################### Future Work / Explorations #########################
#
# Note: These are not all setup usefully yet and some may not be appropriate for a notebook repo.


# Runs pre-commit hook.
_hook: _notify_if_not_root
        @echo "Running git hook from {{local_root}}...\n"
        poetry run git hook run pre-commit

# Setup Repo, Installing Dependencies and Readying venv.
setup:
        poetry check
        poetry install --no-root

# Run Tests.
_test:
        poetry run pytest notebooks/

# Lint code.
_lint:
        poetry run ruff notebooks/

# Type check code.
_type:
        poetry run pyright notebooks/

# Generate Documentation.
_doc:
        poetry run pdoc notebooks/

# Scan for security concerns.
sec-test:
        poetry run bandit -r notebooks/

# TODO: add [confirm] attribute when released
# Warning: Heavy, Opinionated command. Installs Poetry and configs venvs to be local.  Downloads pipx for install, via Homebrew.
[macos]
get-poetry:
        @echo "\n-----\nInstalling and Configuring Poetry. Utilizing Homebrew and PipX\n-----\n"
        brew install pipx
        @echo
        pipx ensurepath
        @echo
        pipx install poetry
        @echo
        poetry config virtualenvs.in-project true
        @echo
        poetry config --list
        @echo
        poetry about
