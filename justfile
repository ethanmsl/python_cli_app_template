# Justfile (Convenience Command Runner) for {{ carnate.project_name }}


# home_dir := env_var('HOME')
local_root := justfile_directory()
invocd_from := invocation_directory()
invoc_is_root := if invocd_from == local_root { "true" } else { "false" }
## ANSI Color Codes for use with echo command
GRN := '\033[0;32m' # Green
BLU := '\033[0;34m' # Blue
PRP := '\033[0;35m' # Purple
BRN := '\033[0;33m' # Brown
CYN := '\033[0;36m' # Cyan
NC := '\033[0m'     # No Color

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

# Open notebook environment, Jupyter Lab, in a web browser.
open: _notify_if_not_root
        @ echo "Opening Jupyter Lab in a Web Browser\n"
        poetry run jupyter lab

# List of common Poetry commands.
poet: _notify_if_not_root
        @ echo "{{GRN}}poetry {{CYN}}shell{{NC}}: enters virtual environment."
        @ echo "{{GRN}}exit{{NC}}: exits a shell, e.g. the virtual environment shell the above command puts you in."
        @ echo "{{GRN}}poetry {{CYN}}run{{NC}}: runs a command using the virtual environment (without switching the user's shell to it)."
        @ echo
        @ echo "{{GRN}}poetry {{CYN}}add {{PRP}}...{{NC}}: adds modules to the project."
        @ echo "{{GRN}}poetry {{CYN}}add {{BRN}}--group=dev {{PRP}}...{{NC}}: adds modules to the project *as Developer Dependencies*"
        @ echo "{{GRN}}poetry {{CYN}}remove {{PRP}}...{{NC}}: removes a dependency."
        @ echo
        @ echo "{{GRN}}poetry {{CYN}}update{{NC}}: updates all dependencies. NOTE: this will only update within semver limits set in pyproject.toml"
        @ echo "{{GRN}}poetry {{CYN}}install{{NC}}: installs all dependencies."
        @ echo "{{GRN}}poetry {{CYN}}build{{NC}}: builds tarball and wheel, for distribution."

# Sync all files in `notebooks/` with Jupytext.  (Create code-only mirrors of Jupyter files.)
jups: _notify_if_not_root && _hydratejups
        #!/bin/bash
        @ echo "Syncing Jupytext versions of all '.ipynb' notebooks...\n"
        set -xeuo pipefail # euo pipefail: fail flags; x: print commands
        for notebook in notebooks/*.ipynb; do
                poetry run jupytext --sync "$notebook" # synch .ju.py & .ipynb files
                poetry run jupytext --set-formats .ipynb,.ju.py:percent "$notebook" # jupytext  % format
        done

# Auto-Gen Files: Add, Commit, and Push all changes.
push-chore: _notify_if_not_root
        @ echo "Auto-Gen File Updates: Committing and Pushing all changes to requirments*.txt & dev_docs/*: {{local_root}}...\n"
        git fetch
        git restore --staged .
        git add requirements* dev_docs/*
        git commit --message "chore(auto-gen): requirements files and dev_docs\n\n[note: this is a templated commit]" --no-verify
        git push

# Runs pre-commit hook. (e.g. formatting, linting, testing, generating documentation, etc.)
ghook: _notify_if_not_root
        @ echo "Running git hook from {{local_root}}...\n"
        poetry run git hook run pre-commit

# Show dependency tree for project.
dep-tree:
        @ echo "Dependency tree for {{local_root}}\n"
        poetry show --tree --verbose --verbose --verbose

# Filtered dependency list results.
dep-filter LITERAL:
        @ echo "Filtered, recursed dependency list for {{local_root}}\n"
        poetry show --verbose --verbose --verbose | grep '{{LITERAL}}'

# Warning: Heavy, Opinionated command. Installs Poetry and configs venvs to be local.  Downloads pipx for install, via Homebrew.
[macos]
[confirm]
get-poetry: && init
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


######################### Clutter Help Docs #########################

notify_text := "\n-----\nNOTE:\n    You are running this command in:\n"+invocd_from+"\n    But it will be run in:\n" +local_root+".\n-----\n"
_notify_if_not_root:
        @ echo '{{ if invoc_is_root == 'true' { "" } else { notify_text } }}'

# Sync all files in `notebooks/` with Jupytext.  (Create code-only mirrors of Jupyter files.)
_hydratejups: _notify_if_not_root
        #!/bin/bash
        @ echo "Syncing Jupytext versions of all '.ipynb' notebooks...\n"
        set -xeuo pipefail # euo pipefail: fail flags; x: print commands
        for notebook in notebooks/*.ju.py; do
                poetry run jupytext --sync "$notebook" # synch .ju.py & .ipynb files
                poetry run jupytext --set-formats .ipynb,.ju.py:percent "$notebook" # jupytext  % format
        done

# Scan for security concerns.
_sec-test:
        poetry run bandit -r notebooks/

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

# Push Jupyter file changes after jupytext syncing.
_push-nb: jups
        @echo "Auto-Gen File Updates: Committing and Pushing all changes to requirments*.txt & dev_docs/*: {{local_root}}...\n"
        git fetch
        git restore --staged .
        git add notebooks/*
        git commit --message "chore(jupyter): Automated Jupyter updates push.\n\n[note: this is a templated commit]" --no-verify
        git push

# Show flattened dependency tree for project. (Useful for piping.)
_show-list:
        @ echo "Dependency list (recursed) for {{local_root}}\n"
        poetry show --verbose --verbose --verbose


######################### Future Work / Explorations #########################
#
# Note: These are not all setup usefully yet and some may not be appropriate for a notebook repo.

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

# Run python file in Poetry venv. Add `-m ` for a module. (`poetry run python3`)
_py +INP: _notify_if_not_root
        @ echo "Running {{INP}} via Python...\n"
        poetry run python3 {{INP}}



        
# # Add User dependencies via Poetry.
# deps-add +USER_DEPS:
#         @ echo "Adding the following user dependencies via Poetry: {{USER_DEPS}} ...\n"
#         poetry add {{USER_DEPS}}
#
# # Add Developer dependencies via Poetry. (e.g. linters, testers)
# deps-add-dev +DEV_DEPS:
#         @ echo "Adding the following developer dependencies via Poetry: {{DEV_DEPS}} ...\n"
#         poetry add --group=dev {{DEV_DEPS}}
#
# # Remove dependencies via Poetry.
# deps-remove +DEPS:
#         @ echo "Removing the following developer dependencies via Poetry: {{DEPS}} ...\n"
#         poetry remove {{DEPS}}
#


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

