import numpy as np
import pandas as pd
import json
import plotly.express as px


def calculate_scenarios():
    config = json.load(open('config.json'))['person1']
    config['growth_std'] = config['growth_std']/np.sqrt(12)  # fact sheets shows annulaised standard devivation...
    periods = (config['age_sim_end'] - config['age_starting'])*12 + 1
    drawdown_start_period = (config['age_retirement'] - config['age_starting'])*12 + 1
    size = (periods, config['number_of_runs'])
    inflation = np.random.normal(config['inflation_mean'], config['inflation_std'], size=size)
    growth = np.random.normal(config['growth_mean'], config['growth_std'], size=size)
    delta_growth = (growth - inflation)/12
    scenarios = np.ones(size)
    scenarios[0,:] = config['amount_starting']
    for p in range(periods)[1:]:
        if drawdown_start_period > p:
            scenarios[p,:] = (scenarios[p-1,:] + config['contribution_monthly']) * (1+delta_growth[p,:])
        else:
            scenarios[p,:] = (scenarios[p-1,:] - config['retirement_drawdown_monthly']) * (1+delta_growth[p,:])
    scenarios[scenarios < 0] = 0
    percentiles = [1,10,25,50,75,90,99]
    scenario_stats = np.percentile(scenarios, percentiles, axis=1)
    plot_data = pd.DataFrame(scenario_stats.T, columns = [f"{p}" for p in percentiles])
    plot_data.head()
    plot_data['age'] = [f"{y:04}-{m:02}" for y in range(config['age_starting'], config['age_sim_end']+1) for m in range(1,13)][0:len(plot_data)]
    plot_data = pd.melt(plot_data, id_vars=['age'], var_name='percentile', value_name='value')
    fig = px.line(plot_data, x='age', y='value', color='percentile')
    fig.write_html("result.html")



if __name__ == '__main__':
    calculate_scenarios()
