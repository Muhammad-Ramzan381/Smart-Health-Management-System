"""
Queue Implementation for Reminder System
Used for managing health reminders and notifications
"""

import heapq
from datetime import datetime


class Queue:
    """Basic FIFO Queue implementation"""

    def __init__(self):
        self.items = []

    def enqueue(self, item):
        """Add item to the end of queue"""
        self.items.append(item)

    def dequeue(self):
        """Remove and return item from front of queue"""
        if self.is_empty():
            return None
        return self.items.pop(0)

    def peek(self):
        """Return front item without removing"""
        if self.is_empty():
            return None
        return self.items[0]

    def is_empty(self):
        """Check if queue is empty"""
        return len(self.items) == 0

    def size(self):
        """Return number of items in queue"""
        return len(self.items)

    def clear(self):
        """Clear all items from queue"""
        self.items = []

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return str(self.items)


class PriorityQueue:
    """Priority Queue using min-heap"""

    def __init__(self):
        self.heap = []
        self.counter = 0  # For stable sorting

    def enqueue(self, item, priority):
        """Add item with priority (lower number = higher priority)"""
        heapq.heappush(self.heap, (priority, self.counter, item))
        self.counter += 1

    def dequeue(self):
        """Remove and return highest priority item"""
        if self.is_empty():
            return None
        priority, counter, item = heapq.heappop(self.heap)
        return item

    def peek(self):
        """Return highest priority item without removing"""
        if self.is_empty():
            return None
        return self.heap[0][2]

    def is_empty(self):
        """Check if queue is empty"""
        return len(self.heap) == 0

    def size(self):
        """Return number of items in queue"""
        return len(self.heap)

    def clear(self):
        """Clear all items from queue"""
        self.heap = []
        self.counter = 0

    def __len__(self):
        return len(self.heap)


# Specialized Queue for Health Reminders
class ReminderQueue(PriorityQueue):
    """Queue for managing health-related reminders"""

    def __init__(self):
        super().__init__()
        self.reminder_id = 0

    def add_reminder(self, message, time_str, priority=5, reminder_type="general"):
        """
        Add a reminder to the queue

        Args:
            message: Reminder message
            time_str: Time string (e.g., "08:00", "14:30")
            priority: 1-10 (1 = urgent, 10 = low priority)
            reminder_type: Type of reminder (diet, remedy, checkup, etc.)
        """
        self.reminder_id += 1
        reminder = {
            'id': self.reminder_id,
            'message': message,
            'time': time_str,
            'priority': priority,
            'type': reminder_type,
            'created_at': datetime.now().isoformat(),
            'completed': False
        }
        self.enqueue(reminder, priority)
        return self.reminder_id

    def get_next_reminder(self):
        """Get the next pending reminder"""
        return self.dequeue()

    def get_all_reminders(self):
        """Get all reminders sorted by priority"""
        reminders = []
        for priority, counter, item in sorted(self.heap):
            reminders.append(item)
        return reminders

    def add_diet_reminder(self, meal_type, foods, time_str):
        """Add a diet-related reminder"""
        message = f"{meal_type}: {', '.join(foods)}"
        return self.add_reminder(message, time_str, priority=3, reminder_type="diet")

    def add_remedy_reminder(self, remedy_name, instructions, time_str):
        """Add a remedy-related reminder"""
        message = f"Take {remedy_name}: {instructions}"
        return self.add_reminder(message, time_str, priority=2, reminder_type="remedy")

    def add_checkup_reminder(self, message, time_str):
        """Add a health checkup reminder"""
        return self.add_reminder(message, time_str, priority=1, reminder_type="checkup")


class SymptomHistoryQueue(Queue):
    """Queue for managing symptom history"""

    def __init__(self, max_size=100):
        super().__init__()
        self.max_size = max_size

    def add_symptom_record(self, symptoms, severity, recommendations):
        """Add a symptom record to history"""
        record = {
            'symptoms': symptoms,
            'severity': severity,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }

        self.enqueue(record)

        # Keep only the most recent records
        while self.size() > self.max_size:
            self.dequeue()

        return record

    def get_history(self, limit=None):
        """Get symptom history (most recent first)"""
        history = list(reversed(self.items))
        if limit:
            return history[:limit]
        return history

    def get_symptom_frequency(self):
        """Analyze frequency of symptoms"""
        frequency = {}
        for record in self.items:
            for symptom in record['symptoms']:
                symptom_lower = symptom.lower()
                if symptom_lower not in frequency:
                    frequency[symptom_lower] = 0
                frequency[symptom_lower] += 1

        # Sort by frequency
        sorted_freq = sorted(
            frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_freq

    def get_recent_symptoms(self, days=7):
        """Get symptoms from the last N days"""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        recent = []

        for record in self.items:
            record_time = datetime.fromisoformat(record['timestamp'])
            if record_time >= cutoff:
                recent.append(record)

        return list(reversed(recent))
