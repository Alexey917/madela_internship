class ProductsAPI:
    def __init__(self, total=12):
        self.total = total

    def get_page(self, limit, page=1):
        start = (page - 1) * limit
        end = min(start + limit, self.total)
        if start >= self.total:
            return []
        return [f"product_{i}" for i in range(start, end)]


class ProductsIterator:
    def __init__(self, api, page_size):
        self.page_size = page_size
        self.page = 1
        self.api = api
        self._done = False 
        

    def __iter__(self):
        return self

    def __next__(self):
        if self.page_size <= 0:
            raise ValueError("page_size must be positive")
        if self._done:
            raise StopIteration
        res = self.api.get_page(self.page_size, self.page)
        if not res:
            raise StopIteration

        if len(res) < self.page_size:
            self._done = True 

        self.page += 1
        return res

api = ProductsAPI()
iterator = ProductsIterator(api, 4)

for it in iterator:
    print(it)

