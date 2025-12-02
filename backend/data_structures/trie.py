"""
Trie (Prefix Tree) Implementation for Autocomplete Functionality
Used for suggesting symptoms as user types
"""

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.word = None  # Store the complete word at end nodes
        self.frequency = 0  # Track how often this word is searched


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0

    def insert(self, word):
        """Insert a word into the trie"""
        if not word:
            return

        node = self.root
        word_lower = word.lower().strip()

        for char in word_lower:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        if not node.is_end_of_word:
            self.word_count += 1

        node.is_end_of_word = True
        node.word = word_lower

    def search(self, word):
        """Check if a word exists in the trie"""
        node = self._find_node(word.lower())
        return node is not None and node.is_end_of_word

    def _find_node(self, prefix):
        """Find the node corresponding to a prefix"""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def starts_with(self, prefix):
        """Check if any word in trie starts with given prefix"""
        return self._find_node(prefix.lower()) is not None

    def autocomplete(self, prefix, max_results=10):
        """Get all words that start with the given prefix"""
        results = []
        node = self._find_node(prefix.lower())

        if node is None:
            return results

        self._collect_words(node, results, max_results)

        # Sort by frequency (most searched first)
        results.sort(key=lambda x: x[1], reverse=True)
        return [word for word, freq in results[:max_results]]

    def _collect_words(self, node, results, max_results):
        """Recursively collect all words from a node"""
        if len(results) >= max_results * 2:  # Collect more for sorting
            return

        if node.is_end_of_word:
            results.append((node.word, node.frequency))

        for char, child_node in node.children.items():
            self._collect_words(child_node, results, max_results)

    def increment_frequency(self, word):
        """Increment the search frequency of a word"""
        node = self._find_node(word.lower())
        if node and node.is_end_of_word:
            node.frequency += 1

    def get_all_words(self):
        """Get all words in the trie"""
        words = []
        self._collect_all_words(self.root, "", words)
        return words

    def _collect_all_words(self, node, current_word, words):
        """Recursively collect all words"""
        if node.is_end_of_word:
            words.append(node.word)

        for char, child_node in node.children.items():
            self._collect_all_words(child_node, current_word + char, words)

    def delete(self, word):
        """Delete a word from the trie"""
        return self._delete_helper(self.root, word.lower(), 0)

    def _delete_helper(self, node, word, index):
        """Helper function for deletion"""
        if index == len(word):
            if not node.is_end_of_word:
                return False
            node.is_end_of_word = False
            node.word = None
            self.word_count -= 1
            return len(node.children) == 0

        char = word[index]
        if char not in node.children:
            return False

        should_delete_child = self._delete_helper(
            node.children[char], word, index + 1
        )

        if should_delete_child:
            del node.children[char]
            return len(node.children) == 0 and not node.is_end_of_word

        return False

    def __len__(self):
        return self.word_count

    def __contains__(self, word):
        return self.search(word)


# Specialized Trie for Symptoms
class SymptomTrie(Trie):
    def __init__(self):
        super().__init__()
        self.symptom_data = {}  # Store additional data for each symptom

    def insert_symptom(self, symptom, severity_range=None, category=None):
        """Insert a symptom with additional metadata"""
        self.insert(symptom)
        self.symptom_data[symptom.lower()] = {
            'severity_range': severity_range or (1, 10),
            'category': category or 'general'
        }

    def get_symptom_data(self, symptom):
        """Get metadata for a symptom"""
        return self.symptom_data.get(symptom.lower())

    def autocomplete_with_data(self, prefix, max_results=10):
        """Get autocomplete suggestions with their metadata"""
        words = self.autocomplete(prefix, max_results)
        return [
            {
                'symptom': word,
                'data': self.symptom_data.get(word, {})
            }
            for word in words
        ]
