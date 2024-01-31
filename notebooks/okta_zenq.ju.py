# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: jp-MarkdownHeadingCollapsed,-all
#     formats: ipynb,.ju.py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Working with Salesforce Data (using Zenq API)
#

# %% [markdown]
# ## Choose whether to make remote calls for data or work with local copy (in `data/no_sync/`)

# %%
from enum import Enum


class RemoteState(Enum):
    """Whether we're fetching data remotely or locally."""
    REMOTE = 0
    LOCAL = 1


# Choose here
data_access_approach = RemoteState.REMOTE
# data_access_approach = RemoteState.LOCAL

# %% [markdown]
# ## Get Secrets for Okta OAuth Call from `.env` and declare headers for re-use
#

# %%
if data_access_approach == RemoteState.REMOTE:
    # Import modules
    import httpx
    import dotenv

    # Grab secrets from .env
    client_id = dotenv.get_key("../.env", "PAGERDUTY_SUPPORT_OKTA_CLIENT_ID")
    client_secret = dotenv.get_key("../.env", "PAGERDUTY_SUPPORT_OKTA_CLIENT_SECRET")
    okta_cookie = dotenv.get_key("../.env", "PAGERDUTY_SUPPORT_OKTA_COOKIE")

    # try headers for okta oauth bearer token
    if client_id is not None and client_secret is not None and okta_cookie is not None:
        headers_okta = {
            "Cookie": okta_cookie,
            "Content-Type": "application/x-www-form-urlencoded",
        }
    else:
        raise EnvironmentError(
            "PAGERDUTY_SUPPORT_OKTA_CLIENT_ID, PAGERDUTY_SUPPORT_OKTA_CLIENT_SECRET, and/or PAGERDUTY_SUPPORT_OKTA_COOKIE not found. Check whether declared in `.env` and dotenv pathing"
        )

    # declare default `headers` value
    if headers_okta is not None:
        headers = headers_okta
        print("`headers` set to `headers_okta` :D")
    else:
        print("No `headers` variable set.  Code below will not run.")

    # Setting Okta Token Base URL
    okta_base_url = "https://pagerduty.okta.com/oauth2/aus1qp12a6efGHJRQ0h8/v1/token"

    # Setting Parameters for Okta Token
    okta_params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "zenq-api",
    }

    ## POST Authorization Code in exchange for a Bearer Access Token
    with httpx.Client() as client:
        getbearer_response = client.post(
            okta_base_url, headers=headers_okta, params=okta_params, timeout=None
        )
    print(f"POST  ../token: {getbearer_response}\n")

    if getbearer_response.is_success:
        dict = getbearer_response.json()
        bearer_token = dict.get("access_token")
    else:
        print("Was NOT a success.")
        print(f"Error: {getbearer_response.status_code}")

    ## Set headers with the Okta Bearer token for re-use

    zenq_base_url = "http://pagerduty-zenq--api.us-e2.cloudhub.io/api/v2/tickets"

    zenq_params = {"status": "'Open'"}

    # try headers for zenq prod
    if bearer_token is not None:
        headers_zenq = {"Authorization": f"{bearer_token}"}
    else:
        print(
            "Bearer token is null. Please check your Okta OAuth API call for more details on a potential issue with receiving the bearer token or refreshing the bearer token."
        )

    # declare default `headers` value
    if headers_zenq is not None:
        headers = headers_zenq
        print("`headers` set to `headers_zenq` :D")
    else:
        print("No `headers` variable set.  Code below will not run.")


# %% [markdown]
# ## Get Data Stored as Dictionary
# (note: this is not an optimized storage format, change to parquet or dataframe at some point)

# %%
import json

if data_access_approach == RemoteState.REMOTE:
    with httpx.Client() as client:
        getzenqprod_response = client.get(
            zenq_base_url, headers=headers_zenq, params=zenq_params, timeout=None
        )
    print(f"GET ../tickets: {getzenqprod_response}\n")

    if getzenqprod_response.is_success:
        zenqueue_dict_list = getzenqprod_response.json()

        with open(
            "../data/no_sync/zenqueue_json_dict.json", "w", encoding="utf-8"
        ) as f:
            json.dump(zenqueue_dict_list, f, ensure_ascii=False, indent=4)
    else:
        dict_list = None
        print("Was NOT a success.")
        raise Exception(f"Error: {getzenqprod_response.status_code}")

elif data_access_approach == RemoteState.LOCAL:
    with open("../data/no_sync/zenqueue_json_dict.json", "r") as f:
        zenqueue_dict_list = json.load(f)


# %% [markdown]
# ## DataFrames Finally! :)

# %%
import polars as pl

print(zenqueue_dict_list)
zqdf = pl.DataFrame(zenqueue_dict_list, infer_schema_length=10000)
zqdf

# %%
zqdf.filter(pl.col("latest_customer_comment").is_not_null())

# %%
zqdf.filter(
    (pl.col("user_email") == "eskowronski-lutz@pagerduty.com")
    | (pl.col("user_email") == "ethanmsl@gmail.com")
)
