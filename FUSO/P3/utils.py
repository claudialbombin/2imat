import numpy as np

def generate_dataset(n,beta=10):
	"""Function to generate a dummy dataset following
	a linear distribution
	
	Args:
		n (int): number of samples to generate
		beta (float): slope
	"""

	# generate n samples:
	
	x = n * np.random.rand(n)
	# add an "error" (noise) to each sample
	std = beta * n / 5
	e = np.random.normal(scale=std, size= n)

	y = x * beta + e
	return x.reshape(-1,1), y