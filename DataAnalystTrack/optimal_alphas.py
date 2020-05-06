# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext_format_version: '1.3'
#   jupytext_formats: py:light
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.6
# ---

import pandas as pd
import numpy as np
import sys
import os
import scipy.interpolate
import datetime
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from merchandising_algos.config import snowflake_dwh_connection
from merchandising_algos.log_setup import setup_logger_to_filename
import seaborn as sns
from logging import getLogger

RECREATE_TABLES = True
CANOE = bool(os.environ.get('IS_CANOE', default=False))
today = datetime.date.today() if CANOE else datetime.datetime(2020, 1, 24).date()
yesterday = (today - datetime.timedelta(days=1))

VALID_BUILD_ENVIRONMENTS = ['production', 'staging', 'dev']
BUILD_ENVIRONMENT = os.environ["ENVIRONMENT"]  # Either "production", "staging" or "dev"
build_env_err_msg = (
    f"The build environment that was given: {BUILD_ENVIRONMENT} is not in the list of "
    f"expected build environments: {', '.join(VALID_BUILD_ENVIRONMENTS)}"
)
assert BUILD_ENVIRONMENT in VALID_BUILD_ENVIRONMENTS, build_env_err_msg
DATABASE = "production" if BUILD_ENVIRONMENT == "production" else "scratch"
SCHEMA = 'merch_algos'

if CANOE:
    conn = snowflake_dwh_connection(warehouse="TRAFFIC_WH", use_sso=False)

    output_path = sys.argv[1]
    ALPHA_TABLE_NAME = 'forecasting_simulation_table_production'
    setup_logger_to_filename(__file__, output_path)
    CREATE_PLOTS = False
else:
    conn = snowflake_dwh_connection(warehouse="BI_DEVELOPMENT", use_sso=True)

    output_path = '../../../data/objective_function/'
    ALPHA_TABLE_NAME = 'alpha_table_development'

os.makedirs(output_path, exist_ok=True)
setup_logger_to_filename('optimal_alphas.py', output_path)
CREATE_PLOTS = True

logger = getLogger("optimal_alphas")
logger.debug(f"output_path: {output_path}")

ov_cp_forecasts_table = pd.read_csv('../results/simulation_results.csv')
ov_cp_forecasts_table.head()

# +
CPPO_WILLING_TO_SPEND = 0.05
ALPHAS_BASELINE = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
ALPHA_BOUNDS = (0.05, 1.0)
LEVEL_TO_OPTIMISE_AT = 'rfm_simple_impute'
LEVELS = list(ov_cp_forecasts_table.sort_values(by=LEVEL_TO_OPTIMISE_AT)[LEVEL_TO_OPTIMISE_AT].unique())
NUM_OF_LEVELS = ov_cp_forecasts_table[LEVEL_TO_OPTIMISE_AT].nunique()

# +
def ov_alpha_function_at_level(alpha_to_evaluate, level_instance):
    """This function makes a prediction of the order volume for a given alpha (alpha_to_evaluate) at level some
    level (level_instance). To do this, we fit a linear splne through the (alpha, ov forecast) coordinates from
    the ov_cp_forecasts_table table, and then predict using this spline at this new alpha_to_evaluate."""

    simulation_df_at_level_instance = ov_cp_forecasts_table.query(f"{LEVEL_TO_OPTIMISE_AT}=='{level_instance}'")

    ov_at_alpha = scipy.interpolate.spline(xk=simulation_df_at_level_instance.alpha,
                                           yk=simulation_df_at_level_instance.ov_prediction,
                                           xnew=alpha_to_evaluate,
                                           order=1)

    return (ov_at_alpha)


def total_ov_over_alphas(alphas_to_evaluate):
    """This function makes a prediction of the total order volume for a given alpha (alpha_to_evaluate) over all levels.
    To do this, we use ov_alpha_function_at_level() and sum across each of the levels."""

    ov_sum = 0
    for level_instance, alpha_instance in zip(LEVELS, alphas_to_evaluate):
        ov_sum = ov_sum + ov_alpha_function_at_level(alpha_instance, level_instance)

    return (ov_sum)
# -

def minus_total_ov_over_alphas(alphas_to_evaluate):
    """This is the negative of the prediction of the total order volume (we want this because we use minimize)."""
    return (-1 * total_ov_over_alphas(alphas_to_evaluate))


# +
def cp_alpha_function_at_level(alpha_to_evaluate, level_instance):
    """This function makes a prediction of the contribution profit for a given alpha (alpha_to_evaluate) at level some
    level (level_instance). To do this, we fit a linear splne through the (alpha, cp forecast) coordinates from
    the ov_cp_forecasts_table table, and then predict using this spline at this new alpha_to_evaluate."""

    simulation_df_at_level_instance = ov_cp_forecasts_table.query(f"{LEVEL_TO_OPTIMISE_AT}=='{level_instance}'")

    cp_at_alpha = scipy.interpolate.spline(xk=simulation_df_at_level_instance.alpha,
                                           yk=simulation_df_at_level_instance.cp_prediction,
                                           xnew=alpha_to_evaluate,
                                           order=1)

    return (cp_at_alpha)

def total_CPPO_over_alphas(alphas_to_evaluate):
    """This function makes a prediction of the total contribution profit per order (CPPO) for a given alpha (alpha_to_evaluate) over all levels.
    To do this, we use cp_alpha_function_at_level() & ov_alpha_function_at_level() and sum across each of the levels."""

    cp_sum = 0
    for level_instance, alpha_instance in zip(LEVELS, alphas_to_evaluate):
        cp_sum = cp_sum + cp_alpha_function_at_level(alpha_instance, level_instance)

    CPPO = cp_sum / total_ov_over_alphas(alphas_to_evaluate)
    return (CPPO)

# +
CPPO_baseline = total_CPPO_over_alphas(ALPHAS_BASELINE) - CPPO_WILLING_TO_SPEND

def total_CPPO_over_alphas_over_benchmark(alphas_to_evaluate):
    """This calculates the foreacasted change in CPPO compared some cppo baseline"""
    return (total_CPPO_over_alphas(alphas_to_evaluate) - CPPO_baseline)

# +
bnds = (ALPHA_BOUNDS,) * NUM_OF_LEVELS
con1 = {'type': 'ineq', 'fun': total_CPPO_over_alphas_over_benchmark}
cons = ([con1])

solution = minimize(
    minus_total_ov_over_alphas,
    ALPHAS_BASELINE,
    bounds=bnds,
    method='SLSQP',
    constraints=cons
)

display(solution)
optimal_alphas = (list(solution.x))
# -


def create_insert_rows_str(alphas):
    """This function takes the optimal alphas and levels and formats them into a string ready to insert into a snowflake dataframe."""
    dummy_index = 0
    total_rows_to_insert_string = ''
    for level_instance, alpha_at_level_instance in zip(LEVELS, alphas):

        row_string = f"(CURRENT_DATE(),  CURRENT_TIMESTAMP(), '{level_instance}',{alpha_at_level_instance})"

        if dummy_index == 0:
            total_rows_to_insert_string = row_string
            dummy_index = 1
        else:
            total_rows_to_insert_string = total_rows_to_insert_string + ',' + row_string

    return (total_rows_to_insert_string)

rows_to_insert_string = create_insert_rows_str(optimal_alphas)
logger.info(f"Rows being inserted into alpha table:{rows_to_insert_string}")

#### The next cell that executes insert_rows_to_alpha_table.sql relies on the assumption that {database}.{schema}.{alpha_table_name} table alreay exists. To create the {schema}.{alpha_table_name}, the commented out python below (in this cell) should be executed (and should only be executed once, as otherwise the former table will be lost). The only scenario when {schema}.{alpha_table_name} should be rerun is for another model that will need it's own alpha lookup table.
#
# # create the {schema}.{alpha_table_name} (ONLY ONCE)
# with open("../fetch_data/sql/create_alpha_table.sql", "r") as f:
#     queries_string = f.read()
# queries_string = queries_string.format(
#     alpha_table_name=ALPHA_TABLE_NAME,
#     database=DATABASE,
#     schema=SCHEMA,
# )
# conn.execute_string(queries_string)
# # create the {schema}.{alpha_table_name} (ONLY ONCE)

if RECREATE_TABLES:
    with open("../fetch_data/sql/insert_rows_to_alpha_table.sql", "r") as f:
        queries_string = f.read()
        queries_string = queries_string.format(
        rows_to_insert=rows_to_insert_string,
        alpha_table_name=ALPHA_TABLE_NAME,
        database=DATABASE,
        schema=SCHEMA,

    )
    conn.execute_string(queries_string)

if CREATE_PLOTS:

    CPPO_willing_to_spend_list = list(np.round(np.linspace(-0.10, 0.10, num=21), 2))

    dummy_index = 0

    for CPPO_change_instance in CPPO_willing_to_spend_list:
        CPPO_baseline = total_CPPO_over_alphas(ALPHAS_BASELINE) - CPPO_change_instance


def total_CPPO_over_alphas_over_benchmark(alphas_to_evaluate):
    return (total_CPPO_over_alphas(alphas_to_evaluate) - CPPO_baseline)


bnds = (ALPHA_BOUNDS,) * NUM_OF_LEVELS
con1 = {'type': 'ineq', 'fun': total_CPPO_over_alphas_over_benchmark}

cons = ([con1])

solution = minimize(minus_total_ov_over_alphas, ALPHAS_BASELINE,
                    bounds=bnds,
                    method='SLSQP',
                    constraints=cons
                    )

display(solution)
optimal_alphas = (list(solution.x))

if dummy_index == 0:

    optimal_alphas_df = pd.DataFrame({LEVEL_TO_OPTIMISE_AT: LEVELS,
                                      'optimal_alphas': optimal_alphas,
                                      'CPPO_change (£)': -CPPO_change_instance
                                      })
    dummy_index = 1
else:
    optimal_alphas_df_tmp = pd.DataFrame({LEVEL_TO_OPTIMISE_AT: LEVELS,
                                          'optimal_alphas': optimal_alphas,
                                          'CPPO_change (£)': -CPPO_change_instance
                                          })

    optimal_alphas_df = pd.concat([optimal_alphas_df, optimal_alphas_df_tmp])

### the change of pCPPO vs. Oprimal alphas.
plt.figure(figsize=(20, 10))
sns.lineplot(data=optimal_alphas_df.round(3), x='CPPO_change (£)', y='optimal_alphas', hue=LEVEL_TO_OPTIMISE_AT,
             markers=True, markersize=10, style=True, linewidth=2);