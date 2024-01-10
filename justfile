# Justfile (Convenience Command Runner) for {{ carnate.project_name }}


# home_dir := env_var('HOME')
local_root := justfile_directory()
invocd_from := invocation_directory()
invoc_is_root := if invocd_from == local_root { "true" } else { "false" }


# Default, lists commands.
_default:
        @ just --list --unsorted

# initialize project
init:
        which just  # in case you're reading ;)
        which pipx
        which poetry
        poetry check
        poetry install
        poetry build
        cp data/template.env .env

# Open Jupyter Lab in a web browser. (`poetry run jupyter lab`)
jupyter: _notify_if_not_root
        @ echo "Opening Jupyter Lab in a Web Browser\n"
        poetry run jupyter lab

# Enter Poetry Virtual Environment. (`poetry shell`)
venv: _notify_if_not_root
        @ echo "Entering Shell running Poetry Virtual Environment\n"
        poetry shell

# Run python file in Poetry venv. Add `-m ` for a module. (`poetry run python3`)
py +INP: _notify_if_not_root
        @ echo "Running {{INP}} via Python...\n"
        poetry run python3 {{INP}}

# Sync all files in `notebooks/` with Jupytext.
jsync-all: _notify_if_not_root
        #!/bin/bash
        @ echo "Syncing Jupytext versions of all '.ipynb' notebooks...\n"
        set -xeuo pipefail # euo pipefail: fail flags; x: print commands
        for notebook in notebooks/*.ipynb; do
                poetry run jupytext --set-formats .ipynb,.ju.py:percent "$notebook" # jupytext  % format
                poetry run jupytext --sync "$notebook" # synch .ju.py & .ipynb files
        done

# Add User dependencies via Poetry.
deps-add +USER_DEPS:
        @ echo "Adding the following user dependencies via Poetry: {{USER_DEPS}} ...\n"
        poetry add {{USER_DEPS}}

# Add Developer dependencies via Poetry. (e.g. linters, testers)
deps-add-dev +DEV_DEPS:
        @ echo "Adding the following developer dependencies via Poetry: {{DEV_DEPS}} ...\n"
        poetry add --group=dev {{DEV_DEPS}}

# Remove dependencies via Poetry.
deps-remove +DEPS:
        @ echo "Removing the following developer dependencies via Poetry: {{DEPS}} ...\n"
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
        @ echo "Auto-Gen File Updates: Committing and Pushing all changes to requirments*.txt & dev_docs/*: {{local_root}}...\n"
        git fetch
        git restore --staged .
        git add requirements* dev_docs/*
        git commit --message "chore(auto-gen): requirements files and dev_docs\n\n[note: this is a templated commit]" --no-verify
        git push

# Show dependency tree for project.
show-tree:
        @ echo "Dependency tree for {{local_root}}\n"
        poetry show --tree --verbose --verbose --verbose

# Filtered dependency list results.
show-filter REGEX:
        @ echo "Filtered, recursed dependency list for {{local_root}}\n"
        poetry show --verbose --verbose --verbose | grep '{{REGEX}}'

notify_text := "\n-----\nNOTE:\n    You are running this command in:\n"+invocd_from+"\n    But it will be run in:\n" +local_root+".\n-----\n"
_notify_if_not_root:
        @ echo '{{ if invoc_is_root == 'true' { "" } else { notify_text } }}'


######################### Clutter Help Docs #########################

# Sync specified files in `notebooks/` with Jupytext.
_jsync +NOTEBOOK: _notify_if_not_root
        @ echo "Creating/Syncing Jupytext versions of the following '.ipynb' notebooks {{NOTEBOOK}}...\n"
        poetry run jupytext --set-formats .ipynb,.ju.py:percent notebooks/{{NOTEBOOK}}.ipynb # jupytext  % format
        poetry run jupytext --sync notebooks/{{NOTEBOOK}}.ipynb # synch .ju.py & .ipynb files

# Update Poetry Dependencies.
_update:
        @ echo "Updating Poetry Virtual Environment...\n"
        @ echo "Note: this will not update versions past the line of what is api-compatible with the version declare in the PyProject.TOML"
        @ echo "e.g. Pydantic v2.x.y will not update past v2, and Poalrs v0.20.z will not update past v0.20; unless PyProject.TOML versions are altered."
        @ echo "This preserves nominal api-compatibility."
        poetry update
        poetry check

# JustFile: Add, Commit, and Push all changes.
_push-justfile: _notify_if_not_root
        @ echo "JustFile Updates: Committing and Pushing all changes to justfile under root: {{local_root}}...\n"
        git fetch
        git restore --staged .
        git add justfile
        git commit --message "build(auto): updates to justfile (command runner)\n\n[note: this is a templated commit message]" --no-verify
        git push

# Show flattened dependency tree for project. (Useful for piping.)
_show-list:
        @ echo "Dependency list (recursed) for {{local_root}}\n"
        poetry show --verbose --verbose --verbose

######################### Future Work / Explorations #########################
#
# Note: These are not all setup usefully yet and some may not be appropriate for a notebook repo.


# TODO: consider running from a `.justscripts` directory 
# See [here](https://just.systems/man/en/chapter_42.html?highlight=bash%20script#safer-bash-shebang-recipes)
#
# Runs pre-commit hook.
_hook: _notify_if_not_root
        @ echo "Running git hook from {{local_root}}...\n"
        poetry run git hook run pre-commit

# Setup Repo, Installing Dependencies and Readying venv.
_setup:
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

# Warning: Heavy, Opinionated command. Installs Poetry and configs venvs to be local.  Downloads pipx for install, via Homebrew.
[macos]
[confirm]
get-poetry:
        @ echo "\n-----\nInstalling and Configuring Poetry. Utilizing Homebrew and PipX\n-----\n"
        brew install pipx
        @ echo
        pipx ensurepath
        @ echo
        pipx install poetry
        @ echo
        poetry config virtualenvs.in-project true
        @ echo
        poetry config --list
        @ echo
        poetry about

# # WARN: doesn't work.  Spawns own shell.  So exit command never exits in the calling shell.
# in_poet_shell := if env_var_or_default('POETRY_ACTIVE', 'false') == '1' { "true" } else { "false" }
# alias exit := exit-poet-shell
# # Exit Poetry venv, if currently in one.
# exit-poet-shell:
#         if {{in_poet_shell}}; then \
#                 echo 'Exiting Poetry Shell (venv)'; \
#                 exit; \
#         else \
#                 echo 'Environment variables do not indicate that we are currently in a Poetry Shell (venv).\n\
#                 You may manually exit any shell with the "exit" command, if you wish!'; \
#         fi

