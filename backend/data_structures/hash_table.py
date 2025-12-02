"""
Hash Table Implementation for O(1) Symptom Lookup
Used for mapping symptoms to diet plans and home remedies
"""

class HashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [[] for _ in range(size)]
        self.count = 0

    def _hash(self, key):
        """Generate hash value for a key"""
        hash_value = 0
        for char in str(key).lower():
            hash_value = (hash_value * 31 + ord(char)) % self.size
        return hash_value

    def insert(self, key, value):
        """Insert a key-value pair into the hash table"""
        index = self._hash(key)

        # Check if key already exists and update
        for i, (k, v) in enumerate(self.table[index]):
            if k.lower() == key.lower():
                # Append to existing list if value is a list
                if isinstance(v, list) and isinstance(value, list):
                    self.table[index][i] = (k, v + value)
                else:
                    self.table[index][i] = (k, value)
                return

        # Insert new key-value pair
        self.table[index].append((key.lower(), value))
        self.count += 1

    def get(self, key):
        """Retrieve value for a given key - O(1) average case"""
        index = self._hash(key)
        for k, v in self.table[index]:
            if k.lower() == key.lower():
                return v
        return None

    def remove(self, key):
        """Remove a key-value pair from the hash table"""
        index = self._hash(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k.lower() == key.lower():
                del self.table[index][i]
                self.count -= 1
                return True
        return False

    def contains(self, key):
        """Check if key exists in hash table"""
        return self.get(key) is not None

    def keys(self):
        """Return all keys in the hash table"""
        all_keys = []
        for bucket in self.table:
            for k, v in bucket:
                all_keys.append(k)
        return all_keys

    def values(self):
        """Return all values in the hash table"""
        all_values = []
        for bucket in self.table:
            for k, v in bucket:
                all_values.append(v)
        return all_values

    def items(self):
        """Return all key-value pairs"""
        all_items = []
        for bucket in self.table:
            for k, v in bucket:
                all_items.append((k, v))
        return all_items

    def __len__(self):
        return self.count

    def __str__(self):
        items = []
        for bucket in self.table:
            for k, v in bucket:
                items.append(f"{k}: {v}")
        return "{" + ", ".join(items) + "}"


# Specialized Hash Table for Symptom-Remedy Mapping
class SymptomHashTable(HashTable):
    def __init__(self):
        super().__init__(size=200)

    def add_remedy(self, symptom, remedy_data):
        """Add a remedy for a symptom"""
        existing = self.get(symptom)
        if existing:
            if isinstance(existing, list):
                existing.append(remedy_data)
                self.insert(symptom, existing)
            else:
                self.insert(symptom, [existing, remedy_data])
        else:
            self.insert(symptom, [remedy_data])

    def get_remedies(self, symptom):
        """Get all remedies for a symptom"""
        result = self.get(symptom)
        if result is None:
            return []
        return result if isinstance(result, list) else [result]

    def search_partial(self, partial_symptom):
        """Search for symptoms containing the partial string"""
        matches = []
        partial_lower = partial_symptom.lower()
        for key in self.keys():
            if partial_lower in key.lower():
                matches.append((key, self.get(key)))
        return matches
