import copy
import uuid
from typing import Dict, List, Any, Optional
import json


class ClusterManager:
    """Main class to handle cluster operations and data management"""

    def __init__(self):
        self.data = {"clusters": []}
        self.history = []
        self.max_history = 10
        self.dragged_member = None
        self.drag_source_cluster = None

    def load_data(self, json_data: Dict) -> tuple[bool, str]:
        """Load and validate JSON data"""
        try:
            # Basic structure validation
            if not isinstance(json_data, dict):
                return False, "invalid_json"

            if "clusters" not in json_data:
                return False, "missing_clusters"

            if not isinstance(json_data["clusters"], list):
                return False, "clusters_not_array"

            if len(json_data["clusters"]) == 0:
                return False, "no_clusters"

            # Validate each cluster
            for i, cluster in enumerate(json_data["clusters"]):
                if not isinstance(cluster, dict):
                    return False, "cluster_not_object", {"i": i}

                # Check required keys
                required_keys = ["id", "name", "members"]
                missing_keys = [key for key in required_keys if key not in cluster]
                if missing_keys:
                    return False, "missing_keys", {"i": i, "missing_keys": missing_keys}

                # Validate members
                if not isinstance(cluster["members"], list):
                    return False, "members_not_array", {"i": i}

                # Validate each member
                for j, member in enumerate(cluster["members"]):
                    if not isinstance(member, dict):
                        return False, "member_not_object", {"i": i, "j": j}

                    member_required = ["id", "name"]
                    member_missing = [
                        key for key in member_required if key not in member
                    ]
                    if member_missing:
                        return (
                            False,
                            "member_missing_keys",
                            {"i": i, "j": j, "member_missing": member_missing},
                        )

                # Ensure relationships key exists
                if "relationships" not in cluster:
                    cluster["relationships"] = []
                elif not isinstance(cluster["relationships"], list):
                    cluster["relationships"] = []

            # Check for duplicate cluster IDs
            cluster_ids = [str(cluster["id"]) for cluster in json_data["clusters"]]
            if len(cluster_ids) != len(set(cluster_ids)):
                return False, "duplicate_ids"

            self.data = json_data
            self.save_state()
            return True, "data_loaded"

        except Exception as e:
            return False, "unexpected_error", {"e": e}

    def save_state(self):
        """Save current state to history"""
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        self.history.append(copy.deepcopy(self.data))

    def undo(self) -> bool:
        """Undo last operation"""
        if len(self.history) > 1:
            self.history.pop()  # Remove current state
            self.data = copy.deepcopy(self.history[-1])
            return True
        return False

    def get_cluster_by_id(self, cluster_id: str) -> Optional[Dict]:
        """Get cluster by ID"""
        for cluster in self.data["clusters"]:
            if str(cluster["id"]) == str(cluster_id):
                return cluster
        return None

    def get_member_by_id(self, cluster_id: str, member_id: str) -> Optional[Dict]:
        """Get member by ID from a specific cluster"""
        cluster = self.get_cluster_by_id(cluster_id)
        if cluster:
            for member in cluster["members"]:
                if str(member["id"]) == str(member_id):
                    return member
        return None

    def get_metrics(self) -> Dict[str, Any]:
        """Calculate cluster metrics"""
        total_clusters = len(self.data["clusters"])
        total_members = sum(
            len(cluster["members"]) for cluster in self.data["clusters"]
        )
        total_relationships = sum(
            len(cluster.get("relationships", [])) for cluster in self.data["clusters"]
        )
        avg_members = total_members / max(total_clusters, 1)

        return {
            "total_clusters": total_clusters,
            "total_members": total_members,
            "avg_members_per_cluster": round(avg_members, 2),
            "total_relationships": total_relationships,
        }

    def search_clusters(self, query: str) -> List[Dict]:
        """Search clusters by name or member name"""
        if not query:
            return self.data["clusters"]

        query = query.lower()
        matching_clusters = []

        for cluster in self.data["clusters"]:
            # Search in cluster name
            if query in cluster["name"].lower():
                matching_clusters.append(cluster)
                continue

            # Search in member names
            for member in cluster["members"]:
                if query in member["name"].lower():
                    matching_clusters.append(cluster)
                    break

        return matching_clusters

    def merge_clusters(self, cluster1_id: str, cluster2_id: str, new_name: str) -> bool:
        """Merge two clusters into one"""
        try:
            cluster1 = self.get_cluster_by_id(cluster1_id)
            cluster2 = self.get_cluster_by_id(cluster2_id)

            if not cluster1 or not cluster2:
                return False

            self.save_state()

            # Combine members (remove duplicates by ID)
            existing_member_ids = {str(m["id"]) for m in cluster1["members"]}
            for member in cluster2["members"]:
                if str(member["id"]) not in existing_member_ids:
                    cluster1["members"].append(member)

            # Combine relationships (remove duplicates and self-references)
            combined_relationships = set(cluster1.get("relationships", []))
            combined_relationships.update(cluster2.get("relationships", []))
            combined_relationships.discard(cluster1_id)
            combined_relationships.discard(cluster2_id)

            cluster1["relationships"] = list(combined_relationships)
            cluster1["name"] = new_name

            # Remove cluster2 and update relationships pointing to it
            self.data["clusters"] = [
                c for c in self.data["clusters"] if str(c["id"]) != str(cluster2_id)
            ]

            # Update relationships in other clusters
            for cluster in self.data["clusters"]:
                if str(cluster2_id) in cluster.get("relationships", []):
                    cluster["relationships"].remove(str(cluster2_id))
                    if str(cluster1_id) not in cluster["relationships"]:
                        cluster["relationships"].append(str(cluster1_id))

            return True
        except Exception:
            return False

    def move_members(
        self, source_cluster_id: str, target_cluster_id: str, member_ids: List[str]
    ) -> bool:
        """Move members from source to target cluster"""
        try:
            source_cluster = self.get_cluster_by_id(source_cluster_id)
            target_cluster = self.get_cluster_by_id(target_cluster_id)

            if not source_cluster or not target_cluster:
                return False

            self.save_state()

            # Find members to move
            members_to_move = []
            remaining_members = []

            for member in source_cluster["members"]:
                if str(member["id"]) in member_ids:
                    members_to_move.append(member)
                else:
                    remaining_members.append(member)

            if not members_to_move:
                return False

            # Update clusters
            source_cluster["members"] = remaining_members
            target_cluster["members"].extend(members_to_move)

            return True
        except Exception:
            return False

    def split_cluster(
        self, cluster_id: str, member_ids: List[str], new_cluster_name: str
    ) -> bool:
        """Split cluster by moving selected members to a new cluster"""
        try:
            source_cluster = self.get_cluster_by_id(cluster_id)
            if not source_cluster:
                return False

            self.save_state()

            # Create new cluster
            new_cluster_id = str(uuid.uuid4())[:8]
            members_to_move = []
            remaining_members = []

            for member in source_cluster["members"]:
                if str(member["id"]) in member_ids:
                    members_to_move.append(member)
                else:
                    remaining_members.append(member)

            if not members_to_move:
                return False

            # Update source cluster
            source_cluster["members"] = remaining_members

            # Create new cluster
            new_cluster = {
                "id": new_cluster_id,
                "name": new_cluster_name,
                "members": members_to_move,
                "relationships": [],
            }

            self.data["clusters"].append(new_cluster)
            return True
        except Exception:
            return False

    def handle_drag_drop(
        self, source_cluster_id: str, member_id: str, target_cluster_id: str
    ) -> bool:
        """Handle drag and drop operation for moving members"""
        try:
            # Get the member from source cluster
            member = self.get_member_by_id(source_cluster_id, member_id)
            if not member:
                return False

            # Move the member
            success = self.move_members(
                source_cluster_id, target_cluster_id, [member_id]
            )
            return success
        except Exception:
            return False
