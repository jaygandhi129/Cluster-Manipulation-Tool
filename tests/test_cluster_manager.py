"""
Tests for the ClusterManager class.
"""

import pytest
import copy
from app.cluster_manager import ClusterManager


class TestClusterManager:
    """Test cases for ClusterManager functionality."""

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return {
            "clusters": [
                {
                    "id": "cluster1",
                    "name": "Test Cluster 1",
                    "members": [
                        {
                            "id": "member1",
                            "name": "John Doe",
                            "metadata": {"role": "Developer"},
                        },
                        {
                            "id": "member2",
                            "name": "Jane Smith",
                            "metadata": {"role": "Designer"},
                        },
                    ],
                    "relationships": ["cluster2"],
                },
                {
                    "id": "cluster2",
                    "name": "Test Cluster 2",
                    "members": [
                        {
                            "id": "member3",
                            "name": "Bob Johnson",
                            "metadata": {"role": "Manager"},
                        }
                    ],
                    "relationships": [],
                },
            ]
        }

    @pytest.fixture
    def manager_with_data(self, sample_data):
        """ClusterManager instance with loaded sample data."""
        manager = ClusterManager()
        manager.load_data(sample_data)
        return manager

    def test_init(self):
        """Test ClusterManager initialization."""
        manager = ClusterManager()
        assert manager.data == {"clusters": []}
        assert manager.history == []
        assert manager.max_history == 10
        assert manager.dragged_member is None
        assert manager.drag_source_cluster is None

    def test_load_valid_data(self, sample_data):
        """Test loading valid cluster data."""
        manager = ClusterManager()
        success, message = manager.load_data(sample_data)

        assert success is True
        assert message == "data_loaded"
        assert len(manager.data["clusters"]) == 2
        assert len(manager.history) == 1

    def test_load_invalid_data_not_dict(self):
        """Test loading invalid data that's not a dictionary."""
        manager = ClusterManager()
        success, message = manager.load_data([1, 2, 3])

        assert success is False
        assert message == "invalid_json"

    def test_load_data_missing_clusters(self):
        """Test loading data without clusters key."""
        manager = ClusterManager()
        success, message = manager.load_data({"data": []})

        assert success is False
        assert message == "missing_clusters"

    def test_load_data_clusters_not_array(self):
        """Test loading data with clusters not being an array."""
        manager = ClusterManager()
        success, message = manager.load_data({"clusters": "not_array"})

        assert success is False
        assert message == "clusters_not_array"

    def test_load_data_no_clusters(self):
        """Test loading data with empty clusters array."""
        manager = ClusterManager()
        success, message = manager.load_data({"clusters": []})

        assert success is False
        assert message == "no_clusters"

    def test_load_data_duplicate_ids(self):
        """Test loading data with duplicate cluster IDs."""
        duplicate_data = {
            "clusters": [
                {"id": "cluster1", "name": "Cluster 1", "members": []},
                {"id": "cluster1", "name": "Cluster 2", "members": []},
            ]
        }
        manager = ClusterManager()
        success, message = manager.load_data(duplicate_data)

        assert success is False
        assert message == "duplicate_ids"

    def test_get_cluster_by_id(self, manager_with_data):
        """Test getting cluster by ID."""
        cluster = manager_with_data.get_cluster_by_id("cluster1")

        assert cluster is not None
        assert cluster["name"] == "Test Cluster 1"
        assert len(cluster["members"]) == 2

    def test_get_cluster_by_id_not_found(self, manager_with_data):
        """Test getting cluster by non-existent ID."""
        cluster = manager_with_data.get_cluster_by_id("nonexistent")
        assert cluster is None

    def test_get_member_by_id(self, manager_with_data):
        """Test getting member by ID from a cluster."""
        member = manager_with_data.get_member_by_id("cluster1", "member1")

        assert member is not None
        assert member["name"] == "John Doe"
        assert member["metadata"]["role"] == "Developer"

    def test_get_member_by_id_not_found(self, manager_with_data):
        """Test getting member by non-existent ID."""
        member = manager_with_data.get_member_by_id("cluster1", "nonexistent")
        assert member is None

    def test_get_metrics(self, manager_with_data):
        """Test getting cluster metrics."""
        metrics = manager_with_data.get_metrics()

        assert metrics["total_clusters"] == 2
        assert metrics["total_members"] == 3
        assert metrics["avg_members_per_cluster"] == 1.5
        assert metrics["total_relationships"] == 1

    def test_search_clusters_by_name(self, manager_with_data):
        """Test searching clusters by cluster name."""
        results = manager_with_data.search_clusters("Test Cluster 1")

        assert len(results) == 1
        assert results[0]["name"] == "Test Cluster 1"

    def test_search_clusters_by_member(self, manager_with_data):
        """Test searching clusters by member name."""
        results = manager_with_data.search_clusters("Jane Smith")

        assert len(results) == 1
        assert results[0]["name"] == "Test Cluster 1"

    def test_search_clusters_no_results(self, manager_with_data):
        """Test searching clusters with no matching results."""
        results = manager_with_data.search_clusters("nonexistent")
        assert len(results) == 0

    def test_search_clusters_empty_query(self, manager_with_data):
        """Test searching clusters with empty query returns all."""
        results = manager_with_data.search_clusters("")
        assert len(results) == 2

    def test_merge_clusters_success(self, manager_with_data):
        """Test successful cluster merge."""
        success = manager_with_data.merge_clusters(
            "cluster1", "cluster2", "Merged Cluster"
        )

        assert success is True
        assert len(manager_with_data.data["clusters"]) == 1

        merged_cluster = manager_with_data.data["clusters"][0]
        assert merged_cluster["name"] == "Merged Cluster"
        assert len(merged_cluster["members"]) == 3

    def test_merge_clusters_invalid_ids(self, manager_with_data):
        """Test merging with invalid cluster IDs."""
        success = manager_with_data.merge_clusters("invalid1", "invalid2", "Merged")
        assert success is False

    def test_move_members_success(self, manager_with_data):
        """Test successful member move."""
        success = manager_with_data.move_members("cluster1", "cluster2", ["member1"])

        assert success is True

        cluster1 = manager_with_data.get_cluster_by_id("cluster1")
        cluster2 = manager_with_data.get_cluster_by_id("cluster2")

        assert len(cluster1["members"]) == 1
        assert len(cluster2["members"]) == 2
        assert cluster2["members"][1]["name"] == "John Doe"

    def test_move_members_invalid_clusters(self, manager_with_data):
        """Test moving members with invalid cluster IDs."""
        success = manager_with_data.move_members("invalid1", "invalid2", ["member1"])
        assert success is False

    def test_split_cluster_success(self, manager_with_data):
        """Test successful cluster split."""
        success = manager_with_data.split_cluster(
            "cluster1", ["member1"], "Split Cluster"
        )

        assert success is True
        assert len(manager_with_data.data["clusters"]) == 3

        # Find the new cluster
        new_cluster = None
        for cluster in manager_with_data.data["clusters"]:
            if cluster["name"] == "Split Cluster":
                new_cluster = cluster
                break

        assert new_cluster is not None
        assert len(new_cluster["members"]) == 1
        assert new_cluster["members"][0]["name"] == "John Doe"

        # Original cluster should have remaining members
        original_cluster = manager_with_data.get_cluster_by_id("cluster1")
        assert len(original_cluster["members"]) == 1
        assert original_cluster["members"][0]["name"] == "Jane Smith"

    def test_split_cluster_invalid_id(self, manager_with_data):
        """Test splitting non-existent cluster."""
        success = manager_with_data.split_cluster("invalid", ["member1"], "Split")
        assert success is False

    def test_split_cluster_no_members_to_move(self, manager_with_data):
        """Test splitting cluster with no valid members to move."""
        success = manager_with_data.split_cluster(
            "cluster1", ["invalid_member"], "Split"
        )
        assert success is False

    def test_undo_operation(self, manager_with_data):
        """Test undo functionality."""
        # Perform an operation
        original_count = len(manager_with_data.data["clusters"])
        manager_with_data.merge_clusters("cluster1", "cluster2", "Merged")
        assert len(manager_with_data.data["clusters"]) == 1

        # Undo the operation
        success = manager_with_data.undo()
        assert success is True
        assert len(manager_with_data.data["clusters"]) == original_count

    def test_undo_no_history(self):
        """Test undo with no history."""
        manager = ClusterManager()
        success = manager.undo()
        assert success is False

    def test_save_state_max_history(self, manager_with_data):
        """Test that history doesn't exceed max_history."""
        manager_with_data.max_history = 2

        # Save multiple states
        for i in range(5):
            manager_with_data.save_state()

        assert len(manager_with_data.history) <= manager_with_data.max_history

    def test_handle_drag_drop_success(self, manager_with_data):
        """Test successful drag and drop operation."""
        success = manager_with_data.handle_drag_drop("cluster1", "member1", "cluster2")

        assert success is True

        cluster1 = manager_with_data.get_cluster_by_id("cluster1")
        cluster2 = manager_with_data.get_cluster_by_id("cluster2")

        assert len(cluster1["members"]) == 1
        assert len(cluster2["members"]) == 2

    def test_handle_drag_drop_invalid_member(self, manager_with_data):
        """Test drag and drop with invalid member."""
        success = manager_with_data.handle_drag_drop("cluster1", "invalid", "cluster2")
        assert success is False
