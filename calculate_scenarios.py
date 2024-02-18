import numpy as np
import pandas as pd
import json
import plotly.express as px
from typing import Tuple


def load_configs(config_file: str = 'config.json') -> dict:
    config = json.load(open(config_file))
    return config


def calculate_transition_dates(age_sim_end: int, age_starting: int, age_retirement: int) -> Tuple[int, int]:
    periods = (age_sim_end - age_starting)*12 + 1
    drawdown_start_period = (age_retirement - age_starting)*12 + 1
    return periods, drawdown_start_period


def calculate_parameters_monthly(parameters_yearly: dict) -> dict:
    parameters_monthly = {}
    parameters_monthly['inflation_mean'] = parameters_yearly['inflation_mean']/12
    parameters_monthly['inflation_std'] = parameters_yearly['inflation_std']/np.sqrt(12)
    parameters_monthly['growth_mean'] = parameters_yearly['growth_mean']/12
    parameters_monthly['growth_std'] = parameters_yearly['growth_std']/np.sqrt(12)
    return parameters_monthly


def plot_scenarios(scenarios: np.array, age_starting: int, age_sim_end: int, percentiles: list = [1,10,25,50,75,90,99]) -> None:
    scenario_stats = np.percentile(scenarios, percentiles, axis=1)
    plot_data = pd.DataFrame(scenario_stats.T, columns = [f"{p}" for p in percentiles])
    plot_data.head()
    plot_data['age'] = [f"{y:04}-{m:02}" for y in range(age_starting, age_sim_end+1) for m in range(1,13)][0:len(plot_data)]
    plot_data = pd.melt(plot_data, id_vars=['age'], var_name='percentile', value_name='value')
    fig = px.line(plot_data, x='age', y='value', color='percentile')
    fig.write_html("result.html")


def calculate_scenarios():
    config = load_configs()
    config = config['person1']  # TODO: loop through multiple
    periods, drawdown_start_period = calculate_transition_dates(config['age_sim_end'], config['age_starting'], config['age_retirement'])
    # config['growth_std'] = config['growth_std']/np.sqrt(12)  # fact sheets shows annulaised standard devivation...
    parameters_monthly = calculate_parameters_monthly(config)

    size = (periods, config['number_of_runs'])
    inflation = np.random.normal(parameters_monthly['inflation_mean'], parameters_monthly['inflation_std'], size=size)
    growth = np.random.normal(parameters_monthly['growth_mean'], parameters_monthly['growth_std'], size=size)
    delta_growth = growth - inflation
    scenarios = np.ones(size)
    scenarios[0,:] = config['amount_starting']
    for p in range(periods)[1:]:
        if drawdown_start_period > p:
            scenarios[p,:] = (scenarios[p-1,:] + config['contribution_monthly']) * (1+delta_growth[p,:])
        else:
            scenarios[p,:] = (scenarios[p-1,:] - config['retirement_drawdown_monthly']) * (1+delta_growth[p,:])
    scenarios[scenarios < 0] = 0
    plot_scenarios(scenarios, config['age_starting'], config['age_sim_end'])


if __name__ == '__main__':
    calculate_scenarios()
