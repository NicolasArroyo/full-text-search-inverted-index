class InvIndexKey:
    def __init__(self, token):
        self.token = token
        self.idf = 0.0

    def __hash__(self) -> int:
        return hash(self.token)

    def __eq__(self, other) -> bool:
        if isinstance(other, InvIndexKey):
            return self.token == other.token
        elif isinstance(other, str):
            return self.token == other
        return False

class InvIndexVal:
    def __init__(self, doc_index, tf):
        self.doc_index = doc_index
        self.tf = tf
        self.tf_idf = 0.0