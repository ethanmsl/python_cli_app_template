# ${{ carnate.project_name }}

<!--toc:start-->

- [${{ carnate.project_name }}](#carnate-projectname)
  - [This project uses the [Just](https://just.systems/), make-like, command runner.](#this-project-uses-the-justhttpsjustsystems-make-like-command-runner)
  - [This project uses [Poetry](https://python-poetry.org/)](#this-project-uses-poetryhttpspython-poetryorg)
  - [This project uses [Jupyter](https://jupyter.org/)](#this-project-uses-jupyterhttpsjupyterorg)
  - [CircleCI Test Status Badge](#circleci-test-status-badge)
  - [Auto-Documentation Link](#auto-documentation-link)
  - [Dev-Dependencies Specified](#dev-dependencies-specified)
  - [Run Pre-Commit Hook Manually](#run-pre-commit-hook-manually)
  - [Dev Notes, Misc.](#dev-notes-misc)
  <!--toc:end-->

## This project uses the [Just](https://just.systems/), make-like, command runner.

You can find a list of [installation methods for various systems here](https://github.com/casey/just#packages).
At the time of generation this specific repo is macos orienteded. `brew install just` or `cargo install just` will be excellent options.
Once installed you can simple run `just` in this directory for a list of configured commands.
(Note: we have _too many_ commands right now. Feedback is welcome and we'll work to winnow them down.)

## This project uses [Poetry](https://python-poetry.org/)

Poetry is for managing python, but is also a python app. We _strongly_ recommend installing it via [pipx](https://pipx.pypa.io/stable/) (which keeps python _applications_' dependencies from interfering with one another.)
For macos users an installation would go as follows:

```shell
brew install pipx
pipx ensurepath
pipx install poetry
poetry config virtualenvs.in-project true
```

Note: we also recommend setting the poetry config option `virtulaenvs.in-project` to `true` (done for you above). This will make hooking up CI/CD pipelines easier.

## This project uses [Jupyter](https://jupyter.org/)

Jupyter is installed and managed by Poetry. So you don't need to worry about it. However, if you like, you can also install it via [pipx](https://pipx.pypa.io/stable/). This can be helpful for casual viewing. (However any sub-dependencies, e.g. seaborn, would also need global access.)

## CircleCI Test Status Badge

To activate:

- In CircleCI go to `Project Settings > Status Badges`
- Click `Add API Token` button
- Click the `Copy` button under `Embed Code` and paste in this README.md file. :)

## Auto-Documentation Link

To activate:

- In GitHub repo go to `settings > pages` Under `Build and deployment` set `Source` to **GitHub Actions**.
- Run the GitHub Action _or_ make any commit to repository
- A new page will be created. Yay!
  - You can place that address in the above link for easy reader navigation.

## Dev-Dependencies Specified

- formatting: `ruff` (replacing `black` & `isort`, beta but acceptable for this functionality)
- linting: `ruff`
- security linting: `bandit`
- lsp & typechecking: `pyright`
- testing: `pytest` + `coverage` (via `pytest-cov`) + `hypothesis`
- auto-documentation: `pdoc` (_not_ ~~"pdoc3"~~, which should be strongly avoided)

(Note: because this repo is now a multi-purpose starter for various projects I've also included numerous data analysis dependencies (`polars`, `scipy`, `jupyter`, `holoviz`, etc.) under dev-dependencies so that they are not accidentally rolled into wheels by someone using the app templating functionality.)

## Run Pre-Commit Hook Manually

from anywhere in project:

```zsh
poetry shell
git hook run pre-commit
```

## Dev Notes, Misc.

Bandit exception syntax:

```python
token_request_prefix = "Token token="  # nosec CWE-259
```

Ruff exception syntax:

```python
token_request_prefix = "Token token="  # noqa: S105
```

Bandit + Ruff exception on same line:

```python
token_request_prefix = "Token token="  # nosec CWE-259  # noqa: S105
```
