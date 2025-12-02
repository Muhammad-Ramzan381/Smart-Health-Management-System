"""
Binary Search Tree Implementation for Sorted Recommendations
Used for organizing diet plans and remedies by effectiveness/priority
"""

class BSTNode:
    def __init__(self, key, data=None):
        self.key = key  # Priority/effectiveness score
        self.data = data  # Remedy or diet plan data
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None
        self.size = 0

    def insert(self, key, data=None):
        """Insert a node with given key and data"""
        new_node = BSTNode(key, data)

        if self.root is None:
            self.root = new_node
            self.size += 1
            return

        current = self.root
        while True:
            if key <= current.key:
                if current.left is None:
                    current.left = new_node
                    self.size += 1
                    return
                current = current.left
            else:
                if current.right is None:
                    current.right = new_node
                    self.size += 1
                    return
                current = current.right

    def search(self, key):
        """Search for a node with given key"""
        current = self.root
        while current:
            if key == current.key:
                return current.data
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None

    def inorder_traversal(self):
        """Return items sorted by key (ascending order)"""
        result = []
        self._inorder_helper(self.root, result)
        return result

    def _inorder_helper(self, node, result):
        """Helper for inorder traversal"""
        if node:
            self._inorder_helper(node.left, result)
            result.append((node.key, node.data))
            self._inorder_helper(node.right, result)

    def reverse_inorder_traversal(self):
        """Return items sorted by key (descending order - highest priority first)"""
        result = []
        self._reverse_inorder_helper(self.root, result)
        return result

    def _reverse_inorder_helper(self, node, result):
        """Helper for reverse inorder traversal"""
        if node:
            self._reverse_inorder_helper(node.right, result)
            result.append((node.key, node.data))
            self._reverse_inorder_helper(node.left, result)

    def get_top_n(self, n):
        """Get top N items by priority (highest first)"""
        items = self.reverse_inorder_traversal()
        return items[:n]

    def get_in_range(self, min_key, max_key):
        """Get all items within a key range"""
        result = []
        self._range_helper(self.root, min_key, max_key, result)
        return result

    def _range_helper(self, node, min_key, max_key, result):
        """Helper for range query"""
        if node is None:
            return

        if min_key < node.key:
            self._range_helper(node.left, min_key, max_key, result)

        if min_key <= node.key <= max_key:
            result.append((node.key, node.data))

        if node.key < max_key:
            self._range_helper(node.right, min_key, max_key, result)

    def find_min(self):
        """Find the minimum key in the tree"""
        if self.root is None:
            return None

        current = self.root
        while current.left:
            current = current.left
        return (current.key, current.data)

    def find_max(self):
        """Find the maximum key in the tree"""
        if self.root is None:
            return None

        current = self.root
        while current.right:
            current = current.right
        return (current.key, current.data)

    def delete(self, key):
        """Delete a node with given key"""
        self.root = self._delete_helper(self.root, key)

    def _delete_helper(self, node, key):
        """Helper for deletion"""
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete_helper(node.left, key)
        elif key > node.key:
            node.right = self._delete_helper(node.right, key)
        else:
            # Node to delete found
            self.size -= 1

            # Case 1: No children
            if node.left is None and node.right is None:
                return None

            # Case 2: One child
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # Case 3: Two children
            # Find inorder successor (smallest in right subtree)
            successor = node.right
            while successor.left:
                successor = successor.left

            node.key = successor.key
            node.data = successor.data
            node.right = self._delete_helper(node.right, successor.key)
            self.size += 1  # Undo the decrement since we're replacing, not removing

        return node

    def __len__(self):
        return self.size

    def is_empty(self):
        return self.root is None


# Specialized BST for Recommendations
class RecommendationBST(BinarySearchTree):
    def __init__(self):
        super().__init__()

    def add_recommendation(self, effectiveness_score, recommendation_data):
        """Add a recommendation with its effectiveness score"""
        self.insert(effectiveness_score, recommendation_data)

    def get_best_recommendations(self, count=5):
        """Get the most effective recommendations"""
        top_items = self.get_top_n(count)
        return [data for score, data in top_items]

    def get_recommendations_by_severity(self, min_severity, max_severity):
        """Get recommendations suitable for a severity range"""
        items = self.get_in_range(min_severity, max_severity)
        # Sort by effectiveness descending
        items.sort(key=lambda x: x[0], reverse=True)
        return [data for score, data in items]

    def get_all_sorted(self):
        """Get all recommendations sorted by effectiveness"""
        return [data for score, data in self.reverse_inorder_traversal()]
