# Manage singletons by name

class Singleton:
    @classmethod
    def get(self, name, newfn):
	"""
	Get a singleton named 'name', creating it
	via newfn() if it doesn't already exist
	"""
	if name not in globals():
	    globals()[name] = newfn()
	return globals()[name]

