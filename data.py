class User:
    def __init__(self, id):
        self.id = id
        self.accounts = []
        self.logic = None
        self.account_id = None

class Account:
    def __init__(self, id):
        self.id = id
        self.dnevnik = None
        self.url = None
        self.oblast = None
        self.okrug = None
        self.sity = None
        self.type = None
        self.school = None
        self.login = None
        self.password = None