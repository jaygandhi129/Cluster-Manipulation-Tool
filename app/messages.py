# Success and error messages for the application

SUCCESS_MESSAGES = {
    "data_loaded": "✅ Data loaded successfully!",
    "operation_undone": "Operation undone!",
    "clusters_merged": "✅ Clusters merged successfully!",
    "members_moved": "✅ Members moved successfully!",
    "cluster_split": "✅ Cluster split successfully!",
    "sample_loaded": "✅ Sample data loaded!",
}

ERROR_MESSAGES = {
    "invalid_json": "❌ Invalid JSON: Root element must be an object",
    "missing_clusters": "❌ Missing required 'clusters' key in JSON",
    "clusters_not_array": "❌ 'clusters' must be an array",
    "no_clusters": "❌ No clusters found in the data",
    "cluster_not_object": "❌ Cluster {i+1} is not a valid object",
    "missing_keys": "❌ Cluster {i+1} missing required keys: {', '.join(missing_keys)}",
    "members_not_array": "❌ Cluster {i+1}: 'members' must be an array",
    "member_not_object": "❌ Cluster {i+1}, Member {j+1} is not a valid object",
    "member_missing_keys": "❌ Cluster {i+1}, Member {j+1} missing: {', '.join(member_missing)}",
    "duplicate_ids": "❌ Duplicate cluster IDs found",
    "unexpected_error": "❌ Unexpected error: {str(e)}",
    "file_too_large": "❌ File too large. Please upload files smaller than 10MB",
    "invalid_json_file": "❌ Invalid JSON file: {str(e)}",
    "encoding_error": "❌ File encoding error. Please ensure your file is UTF-8 encoded",
    "file_processing_error": "❌ Error processing file: {str(e)}",
    "merge_failed": "❌ Failed to merge clusters",
    "move_failed": "❌ Failed to move members",
    "split_failed": "❌ Failed to split cluster",
    "nothing_to_undo": "❌ Nothing to undo",
}

INFO_MESSAGES = {
    "upload_data": "Upload data to see metrics",
    "no_matching_clusters": "No clusters found matching '{search_query}'",
    "need_two_clusters": "Need at least 2 clusters to {operation}",
    "select_different_clusters": "Please select different clusters",
    "no_members_to_move": "Source cluster has no members to move",
    "cannot_move_all": "Cannot move all members. Leave at least one in the original cluster.",
    "min_members_to_split": "Cluster needs at least 2 members to split",
    "upload_data_for_ops": "Upload data to access cluster operations",
    "showing_results": "Showing {count} clusters matching '{query}'",
}
