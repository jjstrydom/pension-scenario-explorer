import json

def initiate_config():
    config = {
        'person1': {
            "age_starting": 24,
            "age_retirement": 60,
            "age_sim_end": 100,
            "number_of_runs": 10000,
            "amount_starting": 0,
            "contribution_monthly": 3500,
            "retirement_drawdown_monthly": 10000,
            "inflation_mean": 0.05,
            "inflation_std":  0.025,
            "growth_mean": 0.10,
            "growth_std": 0.010,
        }
    }
    config_json = json.dumps(config, indent=2)
    with open('config.json', 'w') as outfile:
        outfile.write(config_json)

if __name__ == '__main__':
    initiate_config()
