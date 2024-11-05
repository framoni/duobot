class Node:

    def __init__(self, word, tokens, name="", parent_path=[]):
        self.children = []
        self.name = name
        self.path = parent_path + [name]
        for t in tokens:
            if t == word[:len(t)]:
                tokens_copy = tokens.copy()
                tokens_copy.remove(t)
                self.children.append(Node(word[len(t):], tokens_copy, t, self.path))

    def scan_tree(self, word):
        for c in self.children:
            if "".join(c.path) == word:
                with open("composition.log", "w") as f:
                    f.write(str(c.path))
            c.scan_tree(word)


if __name__ == "__main__":
    n = Node("abcde", ["abcd", "fg", "c", "ab", "de", "bcd"])
    n.scan_tree("abcde")
