class Tag(object):
    pass


class Empty(Tag):

    @staticmethod
    def has(tag):
        False

    @staticmethod
    def add(tag):
        return tag


class And(Tag):

    @staticmethod
    def has(tag):
        return tag is And

    @staticmethod
    def add(tag):
        return AndOr if tag is Or else And


class Or(Tag):

    @staticmethod
    def has(tag):
        return tag is Or

    @staticmethod
    def add(tag):
        return AndOr if tag is And else Or


class AndOr(Tag):

    @staticmethod
    def has(tag):
        return True

    @staticmethod
    def add(tag):
        return AndOr

