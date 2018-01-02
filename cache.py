import tag
import utils


class Cache(object):
    def __init__(self):
        self.db = set()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        key = frozenset(key)
        ans = self._check(key)

        if ans is True:
            self.hits += 1
        else:
            self.misses += 1

        return ans

    def _check(self, key):
        #FIXME: this is very naive, obviously
        superset_check = (
            key.issuperset(stored)
            for stored in self.db)

        return utils.first(
            check is True
            for check in superset_check)
            

    def set(self, key):
        key = frozenset(key)
        self.db.add(key)

    def info(self):
        return {
            "hits": self.hits,
            "misses": self.misses,
            "keys": len(self.db) }

    def __repr__(self):
        return "Cache: {}".format(self.db)


instance = Cache()

