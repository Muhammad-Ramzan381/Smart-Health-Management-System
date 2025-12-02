"""
Data Structures Module for Smart Health Management System
"""

from .hash_table import HashTable, SymptomHashTable
from .trie import Trie, SymptomTrie
from .bst import BinarySearchTree, RecommendationBST
from .graph import Graph, HealthGraph
from .queue import Queue, PriorityQueue, ReminderQueue, SymptomHistoryQueue

__all__ = [
    'HashTable',
    'SymptomHashTable',
    'Trie',
    'SymptomTrie',
    'BinarySearchTree',
    'RecommendationBST',
    'Graph',
    'HealthGraph',
    'Queue',
    'PriorityQueue',
    'ReminderQueue',
    'SymptomHistoryQueue'
]
