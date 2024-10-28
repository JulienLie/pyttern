class MatchSet:
    def __init__(self):
        self.matches = []

    def record(self, match):
        self.matches.append(match)

    def count(self):
        return len(self.matches)
