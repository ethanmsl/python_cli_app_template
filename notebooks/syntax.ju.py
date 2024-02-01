# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
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
#  # Quick Polars Local Test.

# %%
import numpy as np
import polars as pl


# %%
# println!("hi there, from a rust cell");

# %% [markdown]
# # Read Data (classic or planned / "eager" or "lazy")

# %% [markdown]
# ### Classic Loading ("eager")
# `read_...` gives a command to immediately read a file and produce data based on what was read


# %%
# "eager" read
iris_data = pl.read_csv("../data/iris.csv")
print(iris_data)

# %% [markdown]
# ### Planned Loading ("lazy")
# `scan_...` indicates requirements (e.g. data operations should be performed on data from this file)
# when classic data is eventually requested all the requirements (e.g. data from this file, selecting these rows, filtering on those values, etc.) will be processed and a concrete plan executed.  Waiting until all the requirements are specified means the actual plan can be more efficient -- e.g. not reading from columns or rows that won't even be used.

# %%
# "lazy" loading:
# (the plan is used when data itself is requested)
iris_data = pl.scan_csv("../data/iris.csv")
print(iris_data)

# %% [markdown]
# # Print vs Engine-Render

# %%
iris_data = pl.read_csv("../data/iris.csv")
print(iris_data)  # prints out terminal style rendering
iris_data  # uses engine's chosen rendering

# %% [markdown]
# # Combining DataFrames

# %% [markdown]
# ### Joining
# (Left, Right, Inner, Outer)

# %% [markdown]
# Joining two DataFrames on a specified column.

# %%
rng = np.random.default_rng(8)  # generator object

df1 = pl.DataFrame(
    {
        "a": np.arange(0, 8),
        "b": rng.random(8),
        "d": [1, 2.0, np.NaN, np.NaN, 0, -5, -42, None],
    }
)

df2 = pl.DataFrame(
    {
        "x": np.arange(0, 8),
        "y": ["A", "A", "A", "B", "B", "C", "X", "X"],
    }
)

# Join the dataframes
joined = df1.join(df2, left_on="a", right_on="x")
print(joined)


# %% [markdown]
# ### Concatination
# (Horizontal or vertical)

# %%
stacked = df1.hstack(df2)
print(stacked)

# %% [markdown]
# # Various

# %%
iris_type = type(iris_data)
df_type = type(df1)

print(iris_type)
print(df_type)

# %% [markdown]
# # Quick Views
# (Head, Tail, Sample, Describe)

# %% [markdown]
# ### Some Data to Look at

# %% [markdown]
# Creating datetime objects with builtin library. (note that no location is provided by default.)

# %%
import datetime

dfd = pl.DataFrame(
    {
        "integer": [1, 2, 3, 4, 5],
        "date": [
            datetime.datetime(2022, 1, 1),
            datetime.datetime(2022, 1, 2),
            datetime.datetime(2022, 1, 3),
            datetime.datetime(2022, 1, 4),
            datetime.datetime(2022, 1, 5),
        ],
        "float": [4.0, 5.0, 6.0, 7.0, 8.0],
        "words": ["alpha", "beta", "gaga", "delta", "eps"],
    },
)

print(dfd)

# %% [markdown]
# Creating a datetime with the arrow module.  Note that we must exclusively convert to a datetime object.  Also note that a 'default' timezone is provided.

# %%
import arrow

dfd = pl.DataFrame(
    {
        "integer": [1, 2, 3, 4, 5],
        "date": [
            arrow.get("2022-01-01").datetime,
            arrow.get("2022-01-02").datetime,
            arrow.get("2022-01-03").datetime,
            arrow.get("2022-01-04").datetime,
            arrow.get("2022-01-05").datetime,
        ],
        "float": [4.0, 5.0, 6.0, 7.0, 8.0],
        "words": ["alpha", "beta", "gaga", "delta", "eps"],
    },
)

print(dfd)

# %%
print(dfd.head(2))
print(dfd.tail(2))
print(dfd.sample(2))

# %%
print(dfd.glimpse())
dfd.describe()

# %% [markdown]
# # Contexts & Expressions

# %%
dfc = pl.DataFrame(
    {
        "nrs": [1, 2, 3, None, 5],
        "names": ["foo", "ham", "spam", "egg", None],
        "random": np.random.default_rng(5).random(5),
        "groups": ["A", "A", "B", "C", "B"],
    },
)
print(dfc)

# %% [markdown]
# ### Select & With_Columns
# > In the select context the selection applies expressions over columns.
# > The expressions in this context must produce Seriesthat
# > that are all the same length or have a length of 1.
# >
# > A Series of a length of 1 will be broadcasted to match the height of the DataFrame.
# > Note that a select may produce new columns that are
# > aggregations, combinations of expressions, or literals.
#
# `Select`: only returns columns specified
# `With_Columns`: adds specified columns to original

# %%
out_select = dfc.select(
    pl.sum("nrs"),  # note: that it takes original name if not given alias
    pl.col("nrs")
    .sum()
    .alias(
        "same as above",
    ),  # note that the above is a shorthand for this, modulo alias
    pl.col("names").sort(),
    pl.col("names").head(1).alias("first name"),
    (pl.mean("nrs") * 10).alias("10xnrs"),
)
print(out_select)


out_wcol = dfc.with_columns(
    pl.sum("nrs"),  # NOTE!: this ovewrites the original!
    pl.col("nrs")
    .sum()
    .alias(
        "same as above",
    ),  # note that the above is a shorthand for this, modulo alias
    pl.col("names").sort(),
    pl.col("names").head(1).alias("first name"),
    (pl.mean("nrs") * 10).alias("10xnrs"),
)
print(out_wcol)

# %% [markdown]
# # GroupBy

# %% [markdown]
# Generating a DataSet to use:

# %%
scores = {
    "Zone": [
        "North",
        "North",
        "North",
        "South",
        "South",
        "East",
        "East",
        "West",
        "West",
    ],
    "School": [
        "Rushmore",
        "Rushmore",
        "Rushmore",
        "Bayside",
        "Rydell",
        "Shermer",
        "Shermer",
        "Ridgemont",
        "Hogwarts",
    ],
    "Name": ["Jonny", "Mary", "Jim", "Joe", "Jakob", "Jimmy", "Erik", "Lam", "Yip"],
    "Math": [78, 39, 798, 76, 56, 67, 89, 100, 55],
    "Science": [80, 45, 80, 68, 90, 45, 66, 89, 32],
}


school_df = pl.DataFrame(scores)
print(school_df)

# %% [markdown]
# We choose to **group_by** (group *based on*) `zone` (N,S,E,W).
# Then we choose to **agg**regate some columns (all of them in this case) based on that grouping.
# So, for example, the `School` column becomes a list of all the values it previously had, aggregating based on the group_by we chose.

# %%
q = (
    school_df.lazy()
    .group_by(by="Zone")
    .agg(
        "School",
        "Name",
        "Math",
        "Science",
    )
)
q.collect()

# %% [markdown]
# Next we do the same, but also specify what we want to **filter** the data.  Specifically, we only want data where the `Zone` column has the value `East`.
#
# Note: we don't need to concern ourselves with the fact that we aggregated and then filtered.  This uses `.lazy()` methods; so we're merely noting requirements.
# When we call `.collect()` we request that our requirements are met and classic data is generated.  Polars will optimize the query as it's able.

# %%
q = (
    school_df.lazy()
    .group_by(by="Zone")
    .agg(
        "School",
        "Name",
        "Math",
        "Science",
    )
    .filter(pl.col("Zone") == "East")
)
q.collect()

# %% [markdown]
# Again we group by `Zone`, but *this* time we **agg**regate by a new (manufactured) column.
# We create a new column named 'science standard deviation', that originates from the previous.
# The new column knows the origin of its values and provides a standard deviation based on them, in accordance with the Zone values we groupeed by.

# %%
q = (
    school_df.lazy()
    .group_by(by="Zone")
    .agg(
        pl.col("Science").std().alias("Science_std"),
    )
)
q.collect()


# %% [markdown]
# ### Note: order returned by groupby is effectively random
# ###       (presumably due to split-threading)

# %%
q = (
    school_df.lazy()
    .group_by(by="Zone")
    .agg(
        [
            pl.col("Science").count().alias("Number of Schools"),
            pl.col("Science").max().alias("Science(Max)"),
            pl.col("Science").min().alias("Science(Min)"),
            pl.col("Science").mean().alias("Science(Mean)"),
            pl.col("Math").max().alias("Math(Max)"),
            pl.col("Math").min().alias("Math(Min)"),
            pl.col("Math").mean().alias("Math(Mean)"),
        ],
    )
)
print(q.collect())

# %% [markdown]
# ### `.sort()` can be used to deal with the variable ordering

# %%
q = (
    school_df.lazy()
    .group_by(by="Zone")
    .agg(
        [
            pl.col("Science").count().alias("Number of Schools"),
            pl.col("Science").max().alias("Science(Max)"),
            pl.col("Science").min().alias("Science(Min)"),
            pl.col("Science").mean().alias("Science(Mean)"),
            pl.col("Math").max().alias("Math(Max)"),
            pl.col("Math").min().alias("Math(Min)"),
            pl.col("Math").mean().alias("Math(Mean)"),
        ],
    )
    .sort(by="Zone")
)
print(q.collect())

# %% [markdown]
# ### Here's one hack to create custom ordering :
# ### joining another dataframe and hiding an invisible ordering column

# %%
df_sortorder = pl.DataFrame(
    {
        "Zone": ["North", "South", "East", "West"],
        "Zone_order": [0, 1, 2, 3],
    },
).lazy()

q = (
    school_df.lazy()
    .join(df_sortorder, on="Zone", how="left")
    .group_by(by=["Zone", "Zone_order"])
    .agg([pl.max("Science").alias("Science(Max)")])
    .sort("Zone_order")  # we sort on zone_order here
    .select(pl.exclude("Zone_order"))  # and then exclude it
)
q.collect()

# %% [markdown]
# # Insurance CSV

# %%
insurance_df = pl.scan_csv("../data/insurance.csv")
insurance_df.collect()

# %%
(
    pl.scan_csv("../data/insurance.csv")
    .group_by(by="sex")
    .agg(
        [pl.col("charges").sum()],
    )
).collect()

# %% [markdown]
# The logical operation actually creates a boolean value for each entry.  That can act as a value itself.
# It can also be used in a reverse-truthy manner ("numbry"?) allowing calculations or other operations on the values.

# %%
q = (
    pl.scan_csv("../data/insurance.csv")
    .group_by(by="region")
    .agg(
        [
            (pl.col("sex") == "male").alias("is_male"),
            (pl.col("sex") == "male").sum().alias("#of male"),
            (pl.col("sex") == "female").sum().alias("#of female"),
        ],
    )
    .sort(by="region")
)
q.collect()

# %%
q = (
    pl.scan_csv("../data/insurance.csv")
    .group_by(by="region")
    .agg(
        [
            (pl.col("charges").filter(pl.col("sex") == "male"))
            .mean()
            .alias("male_mean_charges"),
            (pl.col("charges").filter(pl.col("sex") == "female"))
            .mean()
            .alias("female_mean_charges"),
            (pl.col("charges").filter(pl.col("sex") == "male")).alias(
                "male_charge_list"
            ),
        ],
    )
    .sort(by="region")
)
q.collect()

# %%
q = (
    pl.scan_csv("../data/insurance.csv")
    .group_by(by="region")
    .agg(
        [
            pl.col("smoker").count().alias("smoker_Q_count"),
            (pl.col("smoker") == "yes").sum().alias("yes_smoker_count"),
            (pl.col("smoker") == "no").sum().alias("no_smoker_count"),
        ],
    )
)

q.collect()

# %% [markdown]
# ### NOTE: `.count()` counts all entries,
# ###       `.sum()` counts all values that are true (assuming a boolean on column)

# %%
q = (
    pl.scan_csv("../data/insurance.csv")
    .group_by(by="region")
    .agg([(pl.col("smoker") == "yes").sum()])
    .sort(by="region")
)
q.collect()

# %% [markdown]
# ### Dealing with Nesting (start...)

# %%
import polars as pl

df = pl.DataFrame(
    {
        "id": [1, 2, 3],
        "name": ["Mercy", "Tomi", "Grace"],
        "hobbies": [["reading", "cooking"], ["running"], ["traveling", "baking"]],
        "favorites": [["pizza", "ice cream"], ["bread"], ["cake", "hamburger"]],
    }
)
print(df)

df_exploded = df.explode(["hobbies", "favorites"])
print(df_exploded)

# %%
df2 = pl.DataFrame(
    {
        "int": [1, 2],
        "str": ["a", "b"],
        "bool": [True, None],
        "list": [[1, 2], [3]],
    }
)

print(df2)

df2new = df2.select(pl.struct(pl.all()).alias("my_struct"))
print(df2new)

# %% [markdown]
# ## Taxi

# %%
# Jan 2023 NYC Taxi Data (Yellowcab)
pl.read_parquet("../data/yellow_tripdata_2023-01.parquet").sample(3)

# %%
# NYC Taxi Zone Data
pl.read_csv("../data/taxi+_zone_lookup.csv").sample(3)


# %%
# Planned Join and Aggregation Query
taxi_plan = (
    pl.scan_parquet("../data/yellow_tripdata_2023-01.parquet")
    .join(
        pl.scan_csv("../data/taxi+_zone_lookup.csv"),
        left_on="PULocationID",
        right_on="LocationID",
    )
    .filter(pl.col("total_amount") > 25)
    .group_by("Zone")
    .agg(
        (
            pl.col("total_amount")
            / (
                pl.col("tpep_dropoff_datetime") - pl.col("tpep_pickup_datetime")
            ).dt.total_minutes()
        )
        .mean()
        .alias("cost_per_minute")
    )
    .sort("cost_per_minute", descending=True)
)

# Display query plan
taxi_plan.show_graph()

# %%
taxi_df = taxi_plan.collect()
print(taxi_df)
