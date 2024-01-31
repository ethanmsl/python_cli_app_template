# ---
# jupyter:
#   jupytext:
#     formats: ipynb,.ju.py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Some Simple PagerDuty Data Pulls

# %% [markdown]
# ## Get API keys from `.env` and declare headers for re-use

# %%
import httpx
import polars as pl
import dotenv

# Note: a `.env` file needs to be made in the root.  The `data/template.env` serves as a template and the `just init` command will auto-copy it, but requires the personal key be specified, of course.
personal_api_key = dotenv.get_key("../.env", "PAGERDUTY_REST_API_KEY")
public_demonstration_api_key = dotenv.get_key(
    "../.env", "PAGERDUTY_API_CONCEPTS_EXAMPLE_KEY"
)


token_request_prefix = "Token token="  # nosec CWE-259  # noqa: S105

# try headers for personal repo
if personal_api_key is not None:
    headers_personal = {
        "Accept": "application/json",
        "Authorization": (token_request_prefix + personal_api_key),
        "Content-Type": "application/json",
    }
else:
    headers_personal = None
    print(
        "PAGERDUTY_REST_API_KEY not found.  Check whether declared in `.env` and dotenv pathing"
    )

# try headers for public example repo
if public_demonstration_api_key is not None:
    headers_publicizable_example = {
        "Accept": "application/json",
        "Authorization": (token_request_prefix + public_demonstration_api_key),
        "Content-Type": "application/json",
    }
else:
    headers_publicizable_example = None
    raise EnvironmentError(
        "PAGERDUTY_API_CONCEPTS_EXAMPLE_KEY not found.  Check whether `.env` was copied from `data/template.env` and dotenv pathing"
    )


# declare default `headers` value
if headers_personal is not None:
    headers = headers_personal
    print("`headers` set to `headers_personal` :)")
elif headers_publicizable_example is not None:
    headers = headers_publicizable_example
    print("`headers` set to `headers_publicizable_example` :)")
else:
    print("No `headers` variable set.  Code below will not run.")

# %% jupyter={"source_hidden": true}
# Setting Base URL
base_url = "https://api.pagerduty.com"
print(base_url)

# %% [markdown]
# #### Manually Switch Headers to Example here if you like

# %%
# headers = headers_personal
headers = headers_publicizable_example

# %% [markdown]
# ## API Calls to DataFrames

# %% [markdown]
# ### GET Users

# %%
with httpx.Client() as client:
    endpoint = "users"
    getuser_response = client.get(base_url + "/" + endpoint, headers=headers)
    print(f"GET ../users: {getuser_response}\n")

    if getuser_response.is_success:
        d_resp = getuser_response.json()
        # print(dict)
        users_df = pl.DataFrame(d_resp.get(endpoint, []))
        print(f"Was success!: {users_df.head(5)}\n")
    else:
        users_df = None
        print("Was NOT a success.")
        print(f"Error: {getuser_response.status_code}")

    endpoint = "licenses"
    lic_alloc_response = client.get(base_url + "/" + endpoint, headers=headers)
    print(f"GET ../licenses response: {lic_alloc_response}\n")

    if lic_alloc_response.is_success:
        d_resp = lic_alloc_response.json()
        # print(dict)
        licenses_df = pl.DataFrame(d_resp.get(endpoint, []))
        print(f"Was success!: {licenses_df}\n")
    else:
        print("Was NOT a success.")
        print(f"Error: {getuser_response.status_code}")

    endpoint = "license_allocations"
    lic_alloc_response = client.get(base_url + "/" + endpoint, headers=headers)
    print(f"GET ..//license_allocations: {lic_alloc_response}\n")

    if lic_alloc_response.is_success:
        d_resp = lic_alloc_response.json()
        lic_allocs = d_resp.get(endpoint, [])
        lic_allocs_df = pl.DataFrame(lic_allocs)
        print(f"Was success!: {lic_allocs_df}\n")
    else:
        print("Was NOT a success.")
        print(f"Error: {getuser_response.status_code}")

# %% [markdown]
# ## Data Display & Exploration

# %%
# users_df.sample(1)
users_df

# %%
licenses_df.head(2)

# %%
lic_allocs_df.tail(3)

# %%
print(lic_allocs_df.select("license"))

# %%
print(lic_allocs_df.select("user"))
