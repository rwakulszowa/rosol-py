from rosol import utils


class BaseCache(object):

    def __init__(self):
        self.db = set()
        self.hits = 0
        self.misses = 0

    def __repr__(self):
        return "Cache: {}".format(self.db)

    def clear(self):
        self.db = set()
        self.hits = 0
        self.misses = 0

    def info(self):
        return {
            "hits": self.hits,
            "misses": self.misses,
            "keys": len(self.db) }


class NoopCache(BaseCache):

    def get(self, key):
        self.misses += 1

    def set(self, key):
        pass


class Cache(BaseCache):

    def get(self, key):
        """
        >>> cache = Cache()
        >>> cache.db.add(frozenset([1,2]))
        >>> cache.get([1])

        >>> cache.get([1,2,3])
        frozenset({1, 2})
        """
        key = frozenset(key)
        match = self._match(key)

        if match:
            self.hits += 1
        else:
            self.misses += 1

        return match

    def _match(self, key):
        #FIXME: this is very naive, obviously
        supersets = (
            stored
            for stored in self.db
            if key.issuperset(stored))

        return utils.first(supersets)

    def set(self, key):
        key = frozenset(key)
        self.db.add(key)


instance = Cache()

