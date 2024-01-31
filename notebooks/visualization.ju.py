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
# # Visualization

# %% [markdown]
# ## Loading simple Palmer's Penguin Data

# %%
import polars as pl

pengs = pl.read_csv("../data/penguins.csv")
pengs.sample(3)

# %% [markdown]
# ### Behold.  Crazy simple plotting.
# Using holoviz as backend.
# No explicit call to holoviz is required, but the library needs to exist in our .venv in order to be called.
#
# Please note how simple and descriptive the plotting syntax is.

# %%
# note: requires pyarrow be installed (not in notebook, but in venv)
pengs.plot.scatter(x="bill_length_mm", y="bill_depth_mm", by="species")

# %% [markdown]
# ### Slightly more complicated plotting
# `holoviz` is also the backend, but here it uses `scipy` to calculate the estimated probability distribution implied by the data.
# No user interaction is required, but if scipy were not loaded into our .venv holoviz wouldn't be able to call it and this would throw an error.
#
# (KDE: kernel density estimate)

# %%
# note: requires scipy be installed (not in notebook, but in venv)
pengs["flipper_length_mm"].plot.kde()

# %%
irisodes = pl.read_csv("../data/iris.csv")
irisodes.sample(3)
irisodes.plot.scatter(x="sepal.length", y="sepal.width", by="variety")

# %% [markdown]
# ## Plotting Temporal Data

# %% [markdown]
# ### Cleaning Up some stocks data
# - convert time strings to DateTimes
# - convert some pretty printed numbers to actual numbers
# - add a column with company name
#   - re-casting that column as a categorical
#     - Note: almost certainly a simpler way to do that, but optimization is for later

# %% [markdown]
# **PagerDuty**

# %%
pduty = (
    pl.scan_csv("../data/stocks/stock_pagerduty.csv")
    .with_columns(
        [
            pl.col("Date").str.strptime(
                pl.Datetime, "%m/%d/%Y"
            ),  # convert string to datetime
            pl.col("Volume")
            .str.replace_all(",", "")
            .cast(pl.UInt32),  # convert "123,456" to uInt
            pl.lit("PagerDuty").alias("Company").cast(pl.Categorical),
        ]
    )
    .collect()
)
print(pduty.sample(3))
print("Full dataframe: ", pduty.shape[0], " rows by ", pduty.shape[1], " cols")
pduty.plot.line(x="Date", y="Open", label="PagerDuty Stock Opening Prices")

# %% [markdown]
# **PetCo** ("WOOF")

# %%
petco = (
    pl.scan_csv("../data/stocks/stock_petco.csv")
    .with_columns(
        [
            pl.col("Date").str.strptime(
                pl.Datetime, "%m/%d/%Y"
            ),  # convert string to datetime
            pl.col("Volume")
            .str.replace_all(",", "")
            .cast(pl.UInt32),  # convert "123,456" to uInt
            pl.lit("PetCo").alias("Company").cast(pl.Categorical),
        ]
    )
    .collect()
)
print(petco.sample(3))
print("Full dataframe: ", petco.shape[0], " rows by ", pduty.shape[1], " cols")
petco.plot.line(x="Date", y="Open", label="PetCo ('woof') Stock Opening Prices")

# %% [markdown]
# ### Concatenate our Data, and plot by the Company Names we added

# %%
pdpc = pl.concat([pduty, petco])
pdpc.plot.line(
    x="Date", y="Open", by="Company", label="PagerDuty & PetCo -  Raw Stock Value"
)

# %% [markdown]
# ### Let's do some basic analysis
# It would be fun to compare stocks on 'their own scale', as it were.
# Let's just pull out a total average and normalize our data by it.
#
# Logic note:
# (If we were looking for subtler effects there would be better ways of doing this that don't succumb to edge effects or temporal outliers, but this is a great, simple scale & shift operation to get a general sense of data.)
#
# Machine note:
# (This is not using Polar's performance optimizations.  As these are separated transforms; vs making using the 'lazy' api to allow internal optimization.  The repeated storage of our means also adds inefficiencies.  Both to storage and, unnecessary, fetch.  But, to make a lesson of it: don't over-optimize when exploring.  Just explore.  There's certainly syntactic learning ahead though.)

# %%

pdpc_means = pdpc.group_by("Company").agg(
    [
        pl.col("Open").mean().alias("mean_open"),
        pl.col("High").mean().alias("mean_high"),
        pl.col("Low").mean().alias("mean_low"),
        pl.col("Close").mean().alias("mean_close"),
    ]
)

pdpc_ext = pdpc.join(pdpc_means, on="Company")


pdpc_ext = pdpc_ext.with_columns(
    [
        (pl.col("Open") / pl.col("mean_open")).alias("normd_open"),
        (pl.col("High") / pl.col("mean_high")).alias("normd_high"),
        (pl.col("Low") / pl.col("mean_low")).alias("normd_low"),
        (pl.col("Close") / pl.col("mean_close")).alias("normd_close"),
    ]
)

pdpc_ext.sample(3)

# %%
pdpc_ext.plot.line(
    x="Date",
    y="normd_open",
    by="Company",
    label="PagerDuty & PetCo -  Normalized Stock Value",
)

# %% [markdown]
# ## Interactives with `Panel`

# %%
# import panel as pn

# %% [markdown]
# ## Other

# %%
import hvplot.polars

pengs.hvplot()

# %%
