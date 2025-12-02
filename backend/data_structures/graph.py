"""
Graph Implementation for Symptom-Remedy Relationships
Used for mapping connections between symptoms, diet plans, and remedies
"""

from collections import deque


class Graph:
    def __init__(self, directed=False):
        self.adjacency_list = {}
        self.directed = directed
        self.node_data = {}  # Store additional data for each node

    def add_node(self, node, data=None):
        """Add a node to the graph"""
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []
            self.node_data[node] = data

    def add_edge(self, node1, node2, weight=1, relationship_type=None):
        """Add an edge between two nodes"""
        # Ensure both nodes exist
        if node1 not in self.adjacency_list:
            self.add_node(node1)
        if node2 not in self.adjacency_list:
            self.add_node(node2)

        # Add edge with weight and relationship type
        edge_data = {
            'node': node2,
            'weight': weight,
            'type': relationship_type
        }
        self.adjacency_list[node1].append(edge_data)

        if not self.directed:
            reverse_edge = {
                'node': node1,
                'weight': weight,
                'type': relationship_type
            }
            self.adjacency_list[node2].append(reverse_edge)

    def get_neighbors(self, node):
        """Get all neighbors of a node"""
        if node not in self.adjacency_list:
            return []
        return self.adjacency_list[node]

    def get_node_data(self, node):
        """Get data associated with a node"""
        return self.node_data.get(node)

    def has_node(self, node):
        """Check if node exists in graph"""
        return node in self.adjacency_list

    def has_edge(self, node1, node2):
        """Check if edge exists between two nodes"""
        if node1 not in self.adjacency_list:
            return False
        return any(edge['node'] == node2 for edge in self.adjacency_list[node1])

    def bfs(self, start_node):
        """Breadth-first search traversal"""
        if start_node not in self.adjacency_list:
            return []

        visited = set()
        queue = deque([start_node])
        result = []

        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                result.append(node)
                for edge in self.adjacency_list[node]:
                    if edge['node'] not in visited:
                        queue.append(edge['node'])

        return result

    def dfs(self, start_node):
        """Depth-first search traversal"""
        if start_node not in self.adjacency_list:
            return []

        visited = set()
        result = []
        self._dfs_helper(start_node, visited, result)
        return result

    def _dfs_helper(self, node, visited, result):
        """Helper for DFS"""
        visited.add(node)
        result.append(node)
        for edge in self.adjacency_list[node]:
            if edge['node'] not in visited:
                self._dfs_helper(edge['node'], visited, result)

    def find_path(self, start, end):
        """Find a path between two nodes using BFS"""
        if start not in self.adjacency_list or end not in self.adjacency_list:
            return None

        visited = set()
        queue = deque([(start, [start])])

        while queue:
            node, path = queue.popleft()
            if node == end:
                return path

            if node not in visited:
                visited.add(node)
                for edge in self.adjacency_list[node]:
                    if edge['node'] not in visited:
                        queue.append((edge['node'], path + [edge['node']]))

        return None

    def get_all_nodes(self):
        """Get all nodes in the graph"""
        return list(self.adjacency_list.keys())

    def get_node_count(self):
        """Get total number of nodes"""
        return len(self.adjacency_list)

    def get_edge_count(self):
        """Get total number of edges"""
        count = sum(len(edges) for edges in self.adjacency_list.values())
        if not self.directed:
            count //= 2
        return count

    def remove_node(self, node):
        """Remove a node and all its edges"""
        if node not in self.adjacency_list:
            return False

        # Remove edges pointing to this node
        for other_node in self.adjacency_list:
            self.adjacency_list[other_node] = [
                edge for edge in self.adjacency_list[other_node]
                if edge['node'] != node
            ]

        # Remove the node itself
        del self.adjacency_list[node]
        if node in self.node_data:
            del self.node_data[node]

        return True

    def remove_edge(self, node1, node2):
        """Remove an edge between two nodes"""
        if node1 in self.adjacency_list:
            self.adjacency_list[node1] = [
                edge for edge in self.adjacency_list[node1]
                if edge['node'] != node2
            ]

        if not self.directed and node2 in self.adjacency_list:
            self.adjacency_list[node2] = [
                edge for edge in self.adjacency_list[node2]
                if edge['node'] != node1
            ]


# Specialized Graph for Health Relationships
class HealthGraph(Graph):
    def __init__(self):
        super().__init__(directed=True)
        self.symptoms = set()
        self.remedies = set()
        self.diet_plans = set()

    def add_symptom(self, symptom, data=None):
        """Add a symptom node"""
        self.add_node(f"symptom:{symptom}", data)
        self.symptoms.add(symptom)

    def add_remedy(self, remedy, data=None):
        """Add a remedy node"""
        self.add_node(f"remedy:{remedy}", data)
        self.remedies.add(remedy)

    def add_diet_plan(self, diet_plan, data=None):
        """Add a diet plan node"""
        self.add_node(f"diet:{diet_plan}", data)
        self.diet_plans.add(diet_plan)

    def link_symptom_to_remedy(self, symptom, remedy, effectiveness=1):
        """Create a relationship between symptom and remedy"""
        self.add_edge(
            f"symptom:{symptom}",
            f"remedy:{remedy}",
            weight=effectiveness,
            relationship_type="treats"
        )

    def link_symptom_to_diet(self, symptom, diet_plan, effectiveness=1):
        """Create a relationship between symptom and diet plan"""
        self.add_edge(
            f"symptom:{symptom}",
            f"diet:{diet_plan}",
            weight=effectiveness,
            relationship_type="helps"
        )

    def link_related_symptoms(self, symptom1, symptom2, strength=1):
        """Link two related symptoms"""
        self.add_edge(
            f"symptom:{symptom1}",
            f"symptom:{symptom2}",
            weight=strength,
            relationship_type="related"
        )
        self.add_edge(
            f"symptom:{symptom2}",
            f"symptom:{symptom1}",
            weight=strength,
            relationship_type="related"
        )

    def get_remedies_for_symptom(self, symptom):
        """Get all remedies for a symptom"""
        symptom_node = f"symptom:{symptom}"
        if not self.has_node(symptom_node):
            return []

        remedies = []
        for edge in self.get_neighbors(symptom_node):
            if edge['node'].startswith("remedy:"):
                remedy_name = edge['node'].replace("remedy:", "")
                remedies.append({
                    'name': remedy_name,
                    'effectiveness': edge['weight'],
                    'data': self.get_node_data(edge['node'])
                })

        # Sort by effectiveness
        remedies.sort(key=lambda x: x['effectiveness'], reverse=True)
        return remedies

    def get_diet_plans_for_symptom(self, symptom):
        """Get all diet plans for a symptom"""
        symptom_node = f"symptom:{symptom}"
        if not self.has_node(symptom_node):
            return []

        diet_plans = []
        for edge in self.get_neighbors(symptom_node):
            if edge['node'].startswith("diet:"):
                diet_name = edge['node'].replace("diet:", "")
                diet_plans.append({
                    'name': diet_name,
                    'effectiveness': edge['weight'],
                    'data': self.get_node_data(edge['node'])
                })

        diet_plans.sort(key=lambda x: x['effectiveness'], reverse=True)
        return diet_plans

    def get_related_symptoms(self, symptom):
        """Get symptoms related to a given symptom"""
        symptom_node = f"symptom:{symptom}"
        if not self.has_node(symptom_node):
            return []

        related = []
        for edge in self.get_neighbors(symptom_node):
            if edge['node'].startswith("symptom:") and edge['type'] == 'related':
                related_symptom = edge['node'].replace("symptom:", "")
                related.append({
                    'symptom': related_symptom,
                    'strength': edge['weight']
                })

        return related

    def get_recommendations_for_symptoms(self, symptoms):
        """Get combined recommendations for multiple symptoms"""
        remedies_scores = {}
        diet_scores = {}

        for symptom in symptoms:
            # Get remedies
            for remedy in self.get_remedies_for_symptom(symptom):
                name = remedy['name']
                if name not in remedies_scores:
                    remedies_scores[name] = {
                        'score': 0,
                        'count': 0,
                        'data': remedy['data']
                    }
                remedies_scores[name]['score'] += remedy['effectiveness']
                remedies_scores[name]['count'] += 1

            # Get diet plans
            for diet in self.get_diet_plans_for_symptom(symptom):
                name = diet['name']
                if name not in diet_scores:
                    diet_scores[name] = {
                        'score': 0,
                        'count': 0,
                        'data': diet['data']
                    }
                diet_scores[name]['score'] += diet['effectiveness']
                diet_scores[name]['count'] += 1

        # Sort by combined score
        remedies_list = [
            {
                'name': name,
                'score': data['score'],
                'matches': data['count'],
                'data': data['data']
            }
            for name, data in remedies_scores.items()
        ]
        remedies_list.sort(key=lambda x: (x['matches'], x['score']), reverse=True)

        diet_list = [
            {
                'name': name,
                'score': data['score'],
                'matches': data['count'],
                'data': data['data']
            }
            for name, data in diet_scores.items()
        ]
        diet_list.sort(key=lambda x: (x['matches'], x['score']), reverse=True)

        return {
            'remedies': remedies_list,
            'diet_plans': diet_list
        }
