# ${{ carnate.project_name }}

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

- formatting: `isort` & `black`
- linting: `pylint`
- lsp & typechecking: `pyright`
- testing: `pytest` + `coverage` (via `pytest-cov`)
- auto-documentation: `pdoc` (_not_ ~~"pdoc3"~~, which should be strongly avoided)

## Run Pre-Commit Hook Manually

from anywhere in project:

```zsh
poetry shell
git hook run pre-commit
```
