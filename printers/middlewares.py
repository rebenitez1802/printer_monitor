
class NavOptionsMiddleware(object):
	

	def process_request(self, request):
		if (request.user.groups.filter(name__in = ['PrinterAdmin', 'SuperAdmin']) or request.user.is_superuser):
			request.showAdmin = True
		else:
			request.showAdmin = False

		return 