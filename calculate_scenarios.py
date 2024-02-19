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
    parameters_monthly['inflation_mean'] = (1+ parameters_yearly['inflation_mean'])**(1/12) - 1
    parameters_monthly['inflation_std'] = parameters_yearly['inflation_std']/np.sqrt(12)
    parameters_monthly['growth_mean'] = (1+ parameters_yearly['growth_mean'])**(1/12) - 1
    parameters_monthly['growth_std'] = parameters_yearly['growth_std']/np.sqrt(12)
    return parameters_monthly


def calculate_scenarios(
            periods: int, 
            drawdown_start_period: int, 
            parameters_monthly: dict, 
            amount_starting: int | float,
            contribution_monthly: int | float,
            retirement_drawdown_monthly: int | float,
            number_of_runs=1000
        ) -> np.array:
    size = (periods, number_of_runs)
    inflation = np.random.normal(parameters_monthly['inflation_mean'], parameters_monthly['inflation_std'], size=size)
    growth = np.random.normal(parameters_monthly['growth_mean'], parameters_monthly['growth_std'], size=size)
    delta_growth = growth - inflation
    scenarios = np.ones(size)
    scenarios[0,:] = amount_starting
    for p in range(periods)[1:]:
        if drawdown_start_period > p:
            scenarios[p,:] = (scenarios[p-1,:] + contribution_monthly) * (1+delta_growth[p,:])
        else:
            scenarios[p,:] = (scenarios[p-1,:] - retirement_drawdown_monthly) * (1+delta_growth[p,:])
    scenarios[scenarios < 0] = 0
    return scenarios


def plot_scenarios(
            scenarios: np.array,
            age_starting: int,
            age_sim_end: int,
            results_filename: str = 'results',
            percentiles: list = [2.5,10,25,50,75,90,97.5]
        ) -> None:
    scenario_stats = np.percentile(scenarios, percentiles, axis=1)
    plot_data = pd.DataFrame(scenario_stats.T, columns = [f"{p}" for p in percentiles])
    plot_data.head()
    plot_data['age'] = [f"{y:04}-{m:02}" for y in range(age_starting, age_sim_end+1) for m in range(1,13)][0:len(plot_data)]
    plot_data = pd.melt(plot_data, id_vars=['age'], var_name='percentile', value_name='value')
    fig = px.line(plot_data, x='age', y='value', color='percentile')
    fig.write_html(f'{results_filename}.html')


def main():
    all_config = load_configs()
    for scenario, config in  all_config.items():
        print(f"running simulation for {scenario}")
        periods, drawdown_start_period = calculate_transition_dates(config['age_sim_end'], config['age_starting'], config['age_retirement'])
        parameters_monthly = calculate_parameters_monthly(config)
        scenarios = calculate_scenarios(
                periods,
                drawdown_start_period,
                parameters_monthly,
                config['amount_starting'],
                config['contribution_monthly'],
                config['retirement_drawdown_monthly'],
                config['number_of_runs']
            )
        plot_scenarios(scenarios, config['age_starting'], config['age_sim_end'], results_filename=scenario)


if __name__ == '__main__':
    main()
