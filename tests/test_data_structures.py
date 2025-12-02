"""
Unit Tests for Data Structures
Tests Hash Table, Trie, BST, Graph, and Queue implementations
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from data_structures import (
    HashTable, SymptomHashTable,
    Trie, SymptomTrie,
    BST, RecommendationBST,
    Graph, HealthGraph,
    Queue, PriorityQueue, ReminderQueue, SymptomHistoryQueue
)


# ==================== Hash Table Tests ====================

class TestHashTable:
    """Tests for basic HashTable implementation"""

    def test_insert_and_get(self):
        """Test basic insert and retrieval"""
        ht = HashTable()
        ht.insert("key1", "value1")
        ht.insert("key2", "value2")

        assert ht.get("key1") == "value1"
        assert ht.get("key2") == "value2"

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist"""
        ht = HashTable()
        assert ht.get("nonexistent") is None

    def test_update_existing_key(self):
        """Test updating an existing key"""
        ht = HashTable()
        ht.insert("key1", "value1")
        ht.insert("key1", "updated_value")

        assert ht.get("key1") == "updated_value"

    def test_remove(self):
        """Test removing a key"""
        ht = HashTable()
        ht.insert("key1", "value1")
        ht.remove("key1")

        assert ht.get("key1") is None

    def test_contains(self):
        """Test contains method"""
        ht = HashTable()
        ht.insert("key1", "value1")

        assert ht.contains("key1") is True
        assert ht.contains("key2") is False

    def test_keys(self):
        """Test getting all keys"""
        ht = HashTable()
        ht.insert("key1", "value1")
        ht.insert("key2", "value2")

        keys = ht.keys()
        assert "key1" in keys
        assert "key2" in keys
        assert len(keys) == 2

    def test_values(self):
        """Test getting all values"""
        ht = HashTable()
        ht.insert("key1", "value1")
        ht.insert("key2", "value2")

        values = ht.values()
        assert "value1" in values
        assert "value2" in values

    def test_collision_handling(self):
        """Test that collisions are handled properly"""
        ht = HashTable(size=1)  # Force collisions
        ht.insert("key1", "value1")
        ht.insert("key2", "value2")
        ht.insert("key3", "value3")

        assert ht.get("key1") == "value1"
        assert ht.get("key2") == "value2"
        assert ht.get("key3") == "value3"


class TestSymptomHashTable:
    """Tests for SymptomHashTable specialized implementation"""

    def test_add_and_get_remedies(self):
        """Test adding and getting remedies for a symptom"""
        sht = SymptomHashTable()
        remedy1 = {"type": "remedy", "data": {"name": "Ginger Tea"}}
        remedy2 = {"type": "remedy", "data": {"name": "Honey Lemon"}}

        sht.add_remedy("headache", remedy1)
        sht.add_remedy("headache", remedy2)

        remedies = sht.get_remedies("headache")
        assert len(remedies) == 2
        assert remedy1 in remedies
        assert remedy2 in remedies

    def test_search_partial(self):
        """Test partial search functionality"""
        sht = SymptomHashTable()
        sht.add_remedy("headache", {"name": "remedy1"})
        sht.add_remedy("head pain", {"name": "remedy2"})
        sht.add_remedy("back pain", {"name": "remedy3"})

        results = sht.search_partial("head")
        assert len(results) == 2


# ==================== Trie Tests ====================

class TestTrie:
    """Tests for basic Trie implementation"""

    def test_insert_and_search(self):
        """Test basic insert and search"""
        trie = Trie()
        trie.insert("hello")
        trie.insert("world")

        assert trie.search("hello") is True
        assert trie.search("world") is True
        assert trie.search("hell") is False

    def test_starts_with(self):
        """Test prefix checking"""
        trie = Trie()
        trie.insert("hello")
        trie.insert("help")
        trie.insert("world")

        assert trie.starts_with("hel") is True
        assert trie.starts_with("wor") is True
        assert trie.starts_with("xyz") is False

    def test_autocomplete(self):
        """Test autocomplete functionality"""
        trie = Trie()
        trie.insert("hello")
        trie.insert("help")
        trie.insert("helmet")
        trie.insert("world")

        results = trie.autocomplete("hel")
        assert len(results) == 3
        assert "hello" in results
        assert "help" in results
        assert "helmet" in results

    def test_autocomplete_max_results(self):
        """Test autocomplete with max results"""
        trie = Trie()
        for i in range(10):
            trie.insert(f"test{i}")

        results = trie.autocomplete("test", max_results=5)
        assert len(results) == 5

    def test_delete(self):
        """Test deleting words from trie"""
        trie = Trie()
        trie.insert("hello")
        trie.insert("help")

        trie.delete("hello")

        assert trie.search("hello") is False
        assert trie.search("help") is True

    def test_get_all_words(self):
        """Test getting all words"""
        trie = Trie()
        words = ["apple", "banana", "cherry"]
        for word in words:
            trie.insert(word)

        all_words = trie.get_all_words()
        for word in words:
            assert word in all_words

    def test_empty_prefix(self):
        """Test autocomplete with empty prefix"""
        trie = Trie()
        trie.insert("hello")
        trie.insert("world")

        results = trie.autocomplete("")
        assert len(results) == 2


class TestSymptomTrie:
    """Tests for SymptomTrie specialized implementation"""

    def test_insert_symptom_with_metadata(self):
        """Test inserting symptom with metadata"""
        st = SymptomTrie()
        st.insert_symptom("headache", severity_range=[1, 10], category="neurological")

        results = st.autocomplete_with_data("head")
        assert len(results) > 0
        assert results[0]['word'] == "headache"
        assert results[0]['category'] == "neurological"


# ==================== BST Tests ====================

class TestBST:
    """Tests for basic BST implementation"""

    def test_insert_and_search(self):
        """Test basic insert and search"""
        bst = BST()
        bst.insert(5, "five")
        bst.insert(3, "three")
        bst.insert(7, "seven")

        assert bst.search(5) == "five"
        assert bst.search(3) == "three"
        assert bst.search(7) == "seven"

    def test_search_nonexistent(self):
        """Test searching for nonexistent key"""
        bst = BST()
        bst.insert(5, "five")

        assert bst.search(10) is None

    def test_inorder_traversal(self):
        """Test inorder traversal returns sorted order"""
        bst = BST()
        values = [5, 3, 7, 1, 9, 4, 6]
        for v in values:
            bst.insert(v, str(v))

        result = bst.inorder_traversal()
        keys = [node[0] for node in result]

        assert keys == sorted(keys)

    def test_reverse_inorder_traversal(self):
        """Test reverse inorder traversal returns descending order"""
        bst = BST()
        values = [5, 3, 7, 1, 9]
        for v in values:
            bst.insert(v, str(v))

        result = bst.reverse_inorder_traversal()
        keys = [node[0] for node in result]

        assert keys == sorted(keys, reverse=True)

    def test_get_top_n(self):
        """Test getting top N elements"""
        bst = BST()
        for i in range(10):
            bst.insert(i, f"value{i}")

        top_5 = bst.get_top_n(5)
        assert len(top_5) == 5
        # Top should be highest keys
        keys = [node[0] for node in top_5]
        assert keys == [9, 8, 7, 6, 5]

    def test_find_min_max(self):
        """Test finding min and max"""
        bst = BST()
        values = [5, 3, 7, 1, 9]
        for v in values:
            bst.insert(v, str(v))

        min_node = bst.find_min()
        max_node = bst.find_max()

        assert min_node[0] == 1
        assert max_node[0] == 9

    def test_get_in_range(self):
        """Test getting values in range"""
        bst = BST()
        for i in range(10):
            bst.insert(i, f"value{i}")

        in_range = bst.get_in_range(3, 7)
        keys = [node[0] for node in in_range]

        assert all(3 <= k <= 7 for k in keys)


class TestRecommendationBST:
    """Tests for RecommendationBST specialized implementation"""

    def test_add_and_get_recommendations(self):
        """Test adding and getting recommendations"""
        rbst = RecommendationBST()
        rbst.add_recommendation(8, {"name": "Remedy A"})
        rbst.add_recommendation(6, {"name": "Remedy B"})
        rbst.add_recommendation(9, {"name": "Remedy C"})

        best = rbst.get_best_recommendations(2)
        assert len(best) == 2
        # Should return highest effectiveness first
        assert best[0]['name'] == "Remedy C"

    def test_get_all_sorted(self):
        """Test getting all recommendations sorted"""
        rbst = RecommendationBST()
        rbst.add_recommendation(5, {"name": "A"})
        rbst.add_recommendation(8, {"name": "B"})
        rbst.add_recommendation(3, {"name": "C"})

        sorted_recs = rbst.get_all_sorted()
        assert len(sorted_recs) == 3
        # Should be sorted by effectiveness descending
        assert sorted_recs[0]['name'] == "B"


# ==================== Graph Tests ====================

class TestGraph:
    """Tests for basic Graph implementation"""

    def test_add_node(self):
        """Test adding nodes"""
        g = Graph()
        g.add_node("A", {"info": "Node A"})
        g.add_node("B", {"info": "Node B"})

        assert "A" in g.adjacency_list
        assert "B" in g.adjacency_list

    def test_add_edge(self):
        """Test adding edges"""
        g = Graph()
        g.add_node("A")
        g.add_node("B")
        g.add_edge("A", "B", weight=5)

        neighbors = g.get_neighbors("A")
        assert len(neighbors) == 1
        assert neighbors[0]['node'] == "B"
        assert neighbors[0]['weight'] == 5

    def test_bfs(self):
        """Test breadth-first search"""
        g = Graph()
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_node("D")
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")

        visited = g.bfs("A")
        assert "A" in visited
        assert "B" in visited
        assert "C" in visited
        assert "D" in visited

    def test_dfs(self):
        """Test depth-first search"""
        g = Graph()
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_edge("A", "B")
        g.add_edge("B", "C")

        visited = g.dfs("A")
        assert "A" in visited
        assert "B" in visited
        assert "C" in visited

    def test_find_path(self):
        """Test finding path between nodes"""
        g = Graph()
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_edge("A", "B")
        g.add_edge("B", "C")

        path = g.find_path("A", "C")
        assert path is not None
        assert "A" in path
        assert "C" in path

    def test_remove_node(self):
        """Test removing a node"""
        g = Graph()
        g.add_node("A")
        g.add_node("B")
        g.add_edge("A", "B")

        g.remove_node("B")

        assert "B" not in g.adjacency_list
        neighbors = g.get_neighbors("A")
        assert len(neighbors) == 0


class TestHealthGraph:
    """Tests for HealthGraph specialized implementation"""

    def test_add_symptom_and_remedy(self):
        """Test adding symptoms and remedies"""
        hg = HealthGraph()
        hg.add_symptom("headache", {"category": "neurological"})
        hg.add_remedy("Ginger Tea", {"effectiveness": 8})

        assert "symptom:headache" in hg.adjacency_list
        assert "remedy:ginger tea" in hg.adjacency_list

    def test_link_symptom_to_remedy(self):
        """Test linking symptoms to remedies"""
        hg = HealthGraph()
        hg.add_symptom("headache")
        hg.add_remedy("Ginger Tea")
        hg.link_symptom_to_remedy("headache", "Ginger Tea", effectiveness=8)

        remedies = hg.get_remedies_for_symptom("headache")
        assert len(remedies) > 0
        assert remedies[0]['name'].lower() == "ginger tea"

    def test_get_recommendations_for_symptoms(self):
        """Test getting recommendations for multiple symptoms"""
        hg = HealthGraph()
        hg.add_symptom("headache")
        hg.add_symptom("nausea")
        hg.add_remedy("Ginger Tea")
        hg.add_diet_plan("Light Diet")

        hg.link_symptom_to_remedy("headache", "Ginger Tea", effectiveness=8)
        hg.link_symptom_to_remedy("nausea", "Ginger Tea", effectiveness=9)
        hg.link_symptom_to_diet("headache", "Light Diet", effectiveness=7)

        recommendations = hg.get_recommendations_for_symptoms(["headache", "nausea"])

        assert 'remedies' in recommendations
        assert 'diet_plans' in recommendations
        assert len(recommendations['remedies']) > 0

    def test_link_related_symptoms(self):
        """Test linking related symptoms"""
        hg = HealthGraph()
        hg.add_symptom("headache")
        hg.add_symptom("migraine")
        hg.link_related_symptoms("headache", "migraine")

        related = hg.get_related_symptoms("headache")
        assert len(related) > 0
        assert related[0]['symptom'] == "migraine"


# ==================== Queue Tests ====================

class TestQueue:
    """Tests for basic Queue implementation"""

    def test_enqueue_dequeue(self):
        """Test basic enqueue and dequeue"""
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)

        assert q.dequeue() == 1
        assert q.dequeue() == 2
        assert q.dequeue() == 3

    def test_peek(self):
        """Test peek without removing"""
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)

        assert q.peek() == 1
        assert q.size() == 2  # Still has 2 items

    def test_is_empty(self):
        """Test empty check"""
        q = Queue()
        assert q.is_empty() is True

        q.enqueue(1)
        assert q.is_empty() is False

    def test_size(self):
        """Test size tracking"""
        q = Queue()
        assert q.size() == 0

        q.enqueue(1)
        q.enqueue(2)
        assert q.size() == 2

    def test_clear(self):
        """Test clearing queue"""
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.clear()

        assert q.is_empty() is True

    def test_dequeue_empty(self):
        """Test dequeue on empty queue"""
        q = Queue()
        assert q.dequeue() is None


class TestPriorityQueue:
    """Tests for PriorityQueue implementation"""

    def test_priority_ordering(self):
        """Test that items come out in priority order"""
        pq = PriorityQueue()
        pq.enqueue("low", 10)
        pq.enqueue("high", 1)
        pq.enqueue("medium", 5)

        assert pq.dequeue() == "high"
        assert pq.dequeue() == "medium"
        assert pq.dequeue() == "low"

    def test_same_priority(self):
        """Test items with same priority maintain insertion order"""
        pq = PriorityQueue()
        pq.enqueue("first", 5)
        pq.enqueue("second", 5)
        pq.enqueue("third", 5)

        assert pq.dequeue() == "first"
        assert pq.dequeue() == "second"
        assert pq.dequeue() == "third"

    def test_peek(self):
        """Test peek returns highest priority without removing"""
        pq = PriorityQueue()
        pq.enqueue("low", 10)
        pq.enqueue("high", 1)

        assert pq.peek() == "high"
        assert pq.size() == 2


class TestReminderQueue:
    """Tests for ReminderQueue specialized implementation"""

    def test_add_reminder(self):
        """Test adding reminders"""
        rq = ReminderQueue()
        reminder_id = rq.add_reminder("Take medicine", "08:00", priority=2)

        assert reminder_id == 1
        assert rq.size() == 1

    def test_get_next_reminder(self):
        """Test getting next reminder by priority"""
        rq = ReminderQueue()
        rq.add_reminder("Low priority", "10:00", priority=10)
        rq.add_reminder("High priority", "08:00", priority=1)

        next_reminder = rq.get_next_reminder()
        assert next_reminder['message'] == "High priority"

    def test_get_all_reminders(self):
        """Test getting all reminders sorted"""
        rq = ReminderQueue()
        rq.add_reminder("Third", "10:00", priority=3)
        rq.add_reminder("First", "08:00", priority=1)
        rq.add_reminder("Second", "09:00", priority=2)

        all_reminders = rq.get_all_reminders()
        assert len(all_reminders) == 3
        assert all_reminders[0]['message'] == "First"

    def test_add_diet_reminder(self):
        """Test adding diet-specific reminder"""
        rq = ReminderQueue()
        reminder_id = rq.add_diet_reminder("Breakfast", ["Oatmeal", "Fruits"], "08:00")

        all_reminders = rq.get_all_reminders()
        assert all_reminders[0]['type'] == "diet"

    def test_add_remedy_reminder(self):
        """Test adding remedy-specific reminder"""
        rq = ReminderQueue()
        rq.add_remedy_reminder("Ginger Tea", "Drink while warm", "09:00")

        all_reminders = rq.get_all_reminders()
        assert all_reminders[0]['type'] == "remedy"


class TestSymptomHistoryQueue:
    """Tests for SymptomHistoryQueue specialized implementation"""

    def test_add_symptom_record(self):
        """Test adding symptom records"""
        shq = SymptomHistoryQueue()
        record = shq.add_symptom_record(
            ["headache", "nausea"],
            severity=7,
            recommendations={"remedies": 5}
        )

        assert 'symptoms' in record
        assert record['severity'] == 7

    def test_get_history(self):
        """Test getting history (most recent first)"""
        shq = SymptomHistoryQueue()
        shq.add_symptom_record(["first"], 5, {})
        shq.add_symptom_record(["second"], 5, {})
        shq.add_symptom_record(["third"], 5, {})

        history = shq.get_history()
        assert history[0]['symptoms'] == ["third"]  # Most recent

    def test_get_history_with_limit(self):
        """Test getting limited history"""
        shq = SymptomHistoryQueue()
        for i in range(10):
            shq.add_symptom_record([f"symptom{i}"], 5, {})

        history = shq.get_history(limit=5)
        assert len(history) == 5

    def test_max_size_limit(self):
        """Test that max size limit is respected"""
        shq = SymptomHistoryQueue(max_size=5)
        for i in range(10):
            shq.add_symptom_record([f"symptom{i}"], 5, {})

        assert shq.size() == 5

    def test_get_symptom_frequency(self):
        """Test symptom frequency analysis"""
        shq = SymptomHistoryQueue()
        shq.add_symptom_record(["headache"], 5, {})
        shq.add_symptom_record(["headache", "nausea"], 5, {})
        shq.add_symptom_record(["headache"], 5, {})

        frequency = shq.get_symptom_frequency()
        # Should be sorted by frequency
        assert frequency[0][0] == "headache"
        assert frequency[0][1] == 3


# ==================== Integration Tests ====================

class TestDataStructureIntegration:
    """Integration tests combining multiple data structures"""

    def test_full_recommendation_flow(self):
        """Test complete flow from symptom input to recommendations"""
        # Setup
        trie = SymptomTrie()
        hash_table = SymptomHashTable()
        bst = RecommendationBST()
        graph = HealthGraph()

        # Add symptoms to trie
        symptoms = ["headache", "nausea", "fever"]
        for symptom in symptoms:
            trie.insert_symptom(symptom)
            graph.add_symptom(symptom)

        # Add remedies
        remedies = [
            {"name": "Ginger Tea", "effectiveness": 8, "symptoms": ["nausea", "headache"]},
            {"name": "Cold Compress", "effectiveness": 7, "symptoms": ["headache", "fever"]},
        ]

        for remedy in remedies:
            bst.add_recommendation(remedy['effectiveness'], remedy)
            graph.add_remedy(remedy['name'], remedy)
            for symptom in remedy['symptoms']:
                hash_table.add_remedy(symptom, remedy)
                graph.link_symptom_to_remedy(symptom, remedy['name'], remedy['effectiveness'])

        # Test autocomplete
        suggestions = trie.autocomplete("head")
        assert "headache" in suggestions

        # Test hash lookup
        hash_results = hash_table.get_remedies("headache")
        assert len(hash_results) == 2

        # Test BST retrieval
        top_remedies = bst.get_best_recommendations(1)
        assert top_remedies[0]['name'] == "Ginger Tea"

        # Test graph recommendations
        graph_results = graph.get_recommendations_for_symptoms(["headache"])
        assert len(graph_results['remedies']) > 0


# ==================== Run Tests ====================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
