import cmc_helper
from abc import ABC, abstractmethod


class Wrapper(ABC):

	def __init__(self, url: str):
		self._base_url = url

	@property
	def url(self):
		return self._base_url

	@url.setter
	def url(self, value):
		self._base_url = value


class Cmc(Wrapper):

	def __init__(self, url: str):
		super().__init__(url)


base_url = cmc_helper.Urls.base.value
cmc = Cmc(url=base_url)

print(cmc.url)
print(cmc_helper.headers)

# adding params as string query
# sq = urllib.parse.urlencode(params, safe=',"')
# response = self.request_session.get(url=url, params=sq)
