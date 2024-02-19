import numpy as np

nr_runs = 10000
run_length_years = 50
interval = 12
run_length_months = interval*run_length_years

yearly_growth_mean = 0.10
yearly_growth_std = 0.05

monthly_growth_mean = (1 + yearly_growth_mean)**(1/interval) - 1
monthly_growth_std = yearly_growth_std / np.sqrt(interval)



month_to_month_changes = np.random.normal(monthly_growth_mean, monthly_growth_std, size=(run_length_months, nr_runs))
monthly_values = np.cumprod(1+month_to_month_changes, axis=0)
yearly_values = np.reshape(monthly_values, newshape=(run_length_years, interval, nr_runs))


measured_year_to_year_growth = yearly_values[1:run_length_years,0,:]/yearly_values[:run_length_years-1,0,:] - 1

measured_year_to_year_growth_mean = np.mean(measured_year_to_year_growth)
measured_year_to_year_growth_std = np.std(measured_year_to_year_growth)

print(yearly_growth_mean, measured_year_to_year_growth_mean)
print(yearly_growth_std, measured_year_to_year_growth_std)