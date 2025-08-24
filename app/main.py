import streamlit as st
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState

# Import our modules
from cluster_manager import ClusterManager
from messages import SUCCESS_MESSAGES, ERROR_MESSAGES, INFO_MESSAGES
from styles import get_css_styles

# Configure Streamlit page
st.set_page_config(
    page_title="Cluster Manipulation Tool",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS
st.markdown(get_css_styles(), unsafe_allow_html=True)


def create_flow_visualization(
    clusters: List[Dict], search_query: str = ""
) -> StreamlitFlowState:
    """Create flow visualization of clusters using streamlit-flow (v1.6+ compatible)"""
    nodes: List[StreamlitFlowNode] = []
    edges: List[StreamlitFlowEdge] = []

    color_palette = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#FFBE0B",
        "#FB5607",
        "#FF006E",
        "#8338EC",
        "#3A86FF",
    ]

    # --- build nodes ---
    for i, cluster in enumerate(clusters):
        cluster_id = str(cluster["id"])
        member_count = len(cluster["members"])

        is_match = False
        if search_query:
            q = search_query.lower()
            is_match = q in cluster["name"].lower() or any(
                q in m["name"].lower() for m in cluster["members"]
            )

        nodes.append(
            StreamlitFlowNode(
                id=cluster_id,
                pos=(100 + (i % 3) * 300, 100 + (i // 3) * 200),
                data={
                    "label": cluster["name"],
                    "members": cluster["members"],
                    "type": "cluster",
                },
                node_type="default" if member_count > 1 else "input",
                style={
                    "width": 200,
                    "height": max(100, 50 + member_count * 20),
                    "background": (
                        "#FF0000" if is_match else color_palette[i % len(color_palette)]
                    ),
                    "color": "white",
                    "border": "2px solid #FFFFFF",
                    "borderRadius": "10px",
                    "padding": "10px",
                },
                draggable=True,
            )
        )

        # member nodes
        for j, member in enumerate(cluster["members"]):
            nodes.append(
                StreamlitFlowNode(
                    id=f"{cluster_id}_{member['id']}",
                    pos=(110 + (i % 3) * 300, 130 + (i // 3) * 200 + j * 25),
                    data={
                        "label": member["name"],
                        "type": "member",
                        "parent": cluster_id,
                    },
                    node_type="default",
                    style={
                        "width": 180,
                        "height": 20,
                        "background": "#FFFFFF",
                        "color": "#333333",
                        "border": "1px solid #CCCCCC",
                        "borderRadius": "5px",
                        "padding": "2px 5px",
                        "fontSize": "12px",
                    },
                    draggable=True,
                    parent=cluster_id,
                )
            )

    # --- build edges ---
    edge_id = 0
    # use a set of cluster ids present for quick membership checks
    present_clusters = {n.id for n in nodes if n.data.get("type") == "cluster"}
    for cluster in clusters:
        source_id = str(cluster["id"])
        for related_id in cluster.get("relationships", []):
            if related_id in present_clusters:
                edges.append(
                    StreamlitFlowEdge(
                        id=f"edge_{edge_id}",
                        source=source_id,
                        target=related_id,
                        edge_type="smoothstep",
                        style={"stroke": "#CCCCCC", "strokeWidth": 2},
                        animated=False,
                    )
                )
                edge_id += 1

    # --- keep state in session_state to avoid infinite re-render loops ---
    if "flow_state" not in st.session_state:
        st.session_state.flow_state = StreamlitFlowState(nodes, edges)
    else:
        # Re-initialize only if the underlying data really changed.
        # A simple (and cheap) guard: compare counts; replace if different.
        cur = st.session_state.flow_state
        if len(cur.nodes) != len(nodes) or len(cur.edges) != len(edges):
            st.session_state.flow_state = StreamlitFlowState(nodes, edges)

    # Render component (positional args; no extra kwargs)
    updated_state = streamlit_flow("cluster_flow", st.session_state.flow_state)

    # Keep the latest state for the next rerun
    if isinstance(updated_state, StreamlitFlowState):
        st.session_state.flow_state = updated_state

    return st.session_state.flow_state


def handle_flow_events(flow_state: Optional[StreamlitFlowState], cluster_manager):
    """Handle interactions using the returned StreamlitFlowState."""
    if not flow_state:
        return

    # Example pattern: if your state exposes a 'last_interaction' or 'selected_id',
    # you can react to it here. (Exact field names depend on the version;
    # see the Interactions demo/docs.)
    # Pseudocode:
    #
    # selected = getattr(flow_state, "selected_id", None)
    # if selected:
    #     if "_" in selected:
    #         cluster_id, member_id = selected.split("_", 1)
    #         st.session_state.selected_member = {"cluster_id": cluster_id, "member_id": member_id}
    #     else:
    #         st.session_state.selected_cluster = selected


def render_sidebar(cluster_manager):
    """Render the sidebar with metrics and operations"""
    with st.sidebar:
        st.header("📊 Metrics")
        with st.expander(label="Cluster Metrics", expanded=True):

            if cluster_manager.data["clusters"]:
                metrics = cluster_manager.get_metrics()

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Clusters", metrics["total_clusters"])
                    st.metric("Total Members", metrics["total_members"])
                with col2:
                    st.metric("Avg Members/Cluster", metrics["avg_members_per_cluster"])
                    st.metric("Total Relationships", metrics["total_relationships"])
            else:
                st.info(INFO_MESSAGES["upload_data"])

        st.divider()

        # Operations
        st.header("⚙️ Operations")

        if st.button("↩️ Undo Last Operation"):
            if cluster_manager.undo():
                st.success(SUCCESS_MESSAGES["operation_undone"])
                st.rerun()
            else:
                st.warning(ERROR_MESSAGES["nothing_to_undo"])
        # Clear the progress
        if st.button(
            label="🧹 Clear Workbench",
            help="Caution: This will clear all your progress and data.",
        ):
            cluster_manager.data["clusters"] = []
            st.rerun()

        # Export functionality
        if cluster_manager.data["clusters"]:
            st.header("📤 Export")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clusters_updated_{timestamp}.json"

            json_str = json.dumps(cluster_manager.data, indent=2)
            st.download_button(
                label="📥 Download Updated JSON",
                data=json_str,
                file_name=filename,
                mime="application/json",
            )
    return


def render_cluster_operations(cluster_manager):
    """Render the cluster operations panel"""
    if cluster_manager.data["clusters"]:
        st.header("🔧 Cluster Operations")

        # Operation selection
        operation = st.selectbox(
            "Select Operation", ["Merge Clusters", "Move Members", "Split Cluster"]
        )

        clusters = cluster_manager.data["clusters"]
        cluster_options = {
            f"{c['name']} (ID: {c['id']})": str(c["id"]) for c in clusters
        }

        if operation == "Merge Clusters":
            st.subheader("🔗 Merge Two Clusters")

            if len(clusters) < 2:
                st.warning(INFO_MESSAGES["need_two_clusters"].format(operation="merge"))
            else:
                cluster1 = st.selectbox(
                    "Select first cluster",
                    options=list(cluster_options.keys()),
                    key="merge_cluster1",
                )
                cluster2 = st.selectbox(
                    "Select second cluster",
                    options=list(cluster_options.keys()),
                    key="merge_cluster2",
                )
                new_name = st.text_input("New cluster name", value="Merged Cluster")

                if cluster1 != cluster2 and new_name:
                    if st.button("🔗 Merge Clusters", type="primary"):
                        cluster1_id = cluster_options[cluster1]
                        cluster2_id = cluster_options[cluster2]

                        if cluster_manager.merge_clusters(
                            cluster1_id, cluster2_id, new_name
                        ):
                            st.success(SUCCESS_MESSAGES["clusters_merged"])
                            st.rerun()
                        else:
                            st.error(ERROR_MESSAGES["merge_failed"])
                elif cluster1 == cluster2:
                    st.warning(INFO_MESSAGES["select_different_clusters"])

        elif operation == "Move Members":
            st.subheader("🔄 Move Members Between Clusters", width="stretch")

            if len(clusters) < 2:
                st.warning(
                    INFO_MESSAGES["need_two_clusters"].format(operation="move members")
                )
            else:
                source_cluster = st.selectbox(
                    "Source cluster",
                    options=list(cluster_options.keys()),
                    key="move_source",
                )
                target_cluster = st.selectbox(
                    "Target cluster",
                    options=list(cluster_options.keys()),
                    key="move_target",
                )

                if source_cluster != target_cluster:
                    source_cluster_id = cluster_options[source_cluster]
                    source_cluster_obj = cluster_manager.get_cluster_by_id(
                        source_cluster_id
                    )

                    if source_cluster_obj and source_cluster_obj["members"]:
                        member_options = {
                            f"{m['name']} (ID: {m['id']})": str(m["id"])
                            for m in source_cluster_obj["members"]
                        }
                        selected_members = st.multiselect(
                            "Select members to move",
                            options=list(member_options.keys()),
                        )

                        if selected_members:
                            member_ids = [member_options[m] for m in selected_members]

                            if st.button("🔄 Move Members", type="primary"):
                                target_cluster_id = cluster_options[target_cluster]

                                if cluster_manager.move_members(
                                    source_cluster_id, target_cluster_id, member_ids
                                ):
                                    st.success(SUCCESS_MESSAGES["members_moved"])
                                    st.rerun()
                                else:
                                    st.error(ERROR_MESSAGES["move_failed"])
                    else:
                        st.warning(INFO_MESSAGES["no_members_to_move"])
                else:
                    st.warning(INFO_MESSAGES["select_different_clusters"])

        elif operation == "Split Cluster":
            st.subheader("✂️ Split Cluster")

            selected_cluster = st.selectbox(
                "Select cluster to split",
                options=list(cluster_options.keys()),
                key="split_cluster",
            )
            cluster_id = cluster_options[selected_cluster]
            cluster_obj = cluster_manager.get_cluster_by_id(cluster_id)

            if cluster_obj and len(cluster_obj["members"]) > 1:
                member_options = {
                    f"{m['name']} (ID: {m['id']})": str(m["id"])
                    for m in cluster_obj["members"]
                }
                selected_members = st.multiselect(
                    "Select members for new cluster",
                    options=list(member_options.keys()),
                )
                new_cluster_name = st.text_input(
                    "New cluster name", value="Split Cluster"
                )

                if (
                    selected_members
                    and new_cluster_name
                    and len(selected_members) < len(cluster_obj["members"])
                ):
                    member_ids = [member_options[m] for m in selected_members]

                    if st.button("✂️ Split Cluster", type="primary"):
                        if cluster_manager.split_cluster(
                            cluster_id, member_ids, new_cluster_name
                        ):
                            st.success(SUCCESS_MESSAGES["cluster_split"])
                            st.rerun()
                        else:
                            st.error(ERROR_MESSAGES["split_failed"])
                elif len(selected_members) >= len(cluster_obj["members"]):
                    st.warning(INFO_MESSAGES["cannot_move_all"])
            else:
                st.warning(INFO_MESSAGES["min_members_to_split"])
    else:
        st.info(INFO_MESSAGES["upload_data_for_ops"])


def render_data_import(cluster_manager):
    """Render the data import section"""
    if not cluster_manager.data["clusters"]:
        # File upload
        st.header("📁 Data Import")

        # Add sample data option for testing
        col1, col2 = st.columns([3, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "Upload JSON file with cluster data",
                type=["json"],
                help="Upload a JSON file containing cluster data with the required structure",
                accept_multiple_files=False,
            )

        with col2:
            st.write("**Quick Test:**")
            if st.button("🧪 Load Sample Data"):
                try:
                    with open("./data/sample_data.json", "r") as f:
                        sample_data = json.load(f)

                    success, message = cluster_manager.load_data(sample_data)
                    if success:
                        st.success(SUCCESS_MESSAGES["sample_loaded"])
                        st.rerun()
                    else:
                        st.error(ERROR_MESSAGES.get(message, f"Error: {message}"))
                except Exception as e:
                    st.error(f"Error loading sample data: {str(e)}")

        if uploaded_file is not None:
            try:
                # Check file size (limit to 10MB)
                if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
                    st.error(ERROR_MESSAGES["file_too_large"])
                    return

                # Add progress indicator
                with st.spinner("Processing JSON file..."):
                    # Read file content
                    file_content = uploaded_file.read()
                    # Parse JSON
                    json_data = json.loads(file_content.decode("utf-8"))
                    # Validate and load data
                    success, message = cluster_manager.load_data(json_data)

                    if success:
                        st.success(SUCCESS_MESSAGES["data_loaded"])

                        # Show summary of loaded data
                        metrics = cluster_manager.get_metrics()
                        st.info(
                            f"Loaded {metrics['total_clusters']} clusters with {metrics['total_members']} total members"
                        )

                        # Force rerun to update the UI
                        st.rerun()
                    else:
                        # Handle error messages with parameters
                        if isinstance(message, tuple) and len(message) > 1:
                            error_msg = ERROR_MESSAGES.get(message[0], message[0])
                            if len(message) > 2:
                                error_msg = error_msg.format(**message[2])
                            st.error(error_msg)
                        else:
                            st.error(ERROR_MESSAGES.get(message, message))

                        # Show expected structure
                        with st.expander("📋 Expected JSON Structure"):
                            st.code(
                                """
                                {
                                "clusters": [
                                    {
                                    "id": "cluster_1",
                                    "name": "Team Name",
                                    "members": [
                                        {
                                        "id": "member_1",
                                        "name": "Person Name",
                                        "metadata": {"role": "Position"}
                                        }
                                    ],
                                    "relationships": ["cluster_2"]
                                    }
                                ]
                                }""",
                                language="json",
                            )

            except json.JSONDecodeError as e:
                st.error(ERROR_MESSAGES["invalid_json_file"].format(e=str(e)))
                st.info("Please ensure your file contains valid JSON syntax")
            except UnicodeDecodeError:
                st.error(ERROR_MESSAGES["encoding_error"])
            except Exception as e:
                st.error(ERROR_MESSAGES["file_processing_error"].format(e=str(e)))
                st.info("Please check your file format and try again")


def render_cluster_details(cluster_manager, search_query):
    """Render the cluster details section"""
    if cluster_manager.data["clusters"]:
        with st.expander("📋 Cluster wise details", expanded=False):
            # Use filtered clusters if searching
            display_clusters = (
                cluster_manager.search_clusters(search_query)
                if search_query
                else cluster_manager.data["clusters"]
            )

            for i, cluster in enumerate(display_clusters):
                with st.expander(
                    f"🗃️ {cluster['name']} (ID: {cluster['id']}) - {len(cluster['members'])} members"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander("Members", expanded=True, icon="👨‍👩‍👧‍👦"):
                            for member in cluster["members"]:
                                member_info = (
                                    f"• **{member['name']} (ID: {member['id']})**"
                                )
                                st.write(member_info)
                                if "metadata" in member and member["metadata"]:
                                    st.table(member["metadata"])

                    with col2:
                        with st.expander("Relationships", expanded=True, icon="🤝"):
                            if cluster.get("relationships"):
                                for rel_id in cluster["relationships"]:
                                    related_cluster = cluster_manager.get_cluster_by_id(
                                        rel_id
                                    )
                                    if related_cluster:
                                        st.write(
                                            f"• {related_cluster['name']} (ID: {rel_id})"
                                        )
                            else:
                                st.write("No relationships")


def main():
    # Initialize session state
    if "cluster_manager" not in st.session_state:
        st.session_state.cluster_manager = ClusterManager()

    if "selected_clusters" not in st.session_state:
        st.session_state.selected_clusters = []

    if "selected_members" not in st.session_state:
        st.session_state.selected_members = []

    # Header
    st.markdown(
        '<div class="main-header">Clusters Manipulation Tool</div>',
        unsafe_allow_html=True,
    )

    # Get cluster manager instance
    cluster_manager = st.session_state.cluster_manager

    # Render sidebar and get search query
    render_sidebar(cluster_manager)

    search_query = ""

    # Main content
    maincol1, maincol2 = st.columns([30, 8], border=True)

    with maincol1:
        # Data import section
        render_data_import(cluster_manager)

        # Visualization
        if cluster_manager.data["clusters"]:
            col1, col2 = st.columns(2)
            with col1:
                st.header("🌐 Cluster Visualization")
            with col2:
                search_query = st.text_input(
                    "Search clusters or members",
                    placeholder="Enter search term...",
                    icon="🔍",
                )

            # Filter clusters based on search
            filtered_clusters = cluster_manager.search_clusters(search_query)

            if search_query and not filtered_clusters:
                st.warning(
                    INFO_MESSAGES["no_matching_clusters"].format(
                        search_query=search_query
                    )
                )
                filtered_clusters = cluster_manager.data["clusters"]

            flow_state = create_flow_visualization(filtered_clusters, search_query)
            handle_flow_events(flow_state, cluster_manager)

            # Display search results info
            if search_query:
                st.info(
                    INFO_MESSAGES["showing_results"].format(
                        count=len(filtered_clusters), query=search_query
                    )
                )

            # Cluster details section
            render_cluster_details(cluster_manager, search_query)

    with maincol2:
        # Cluster operations panel
        render_cluster_operations(cluster_manager)


if __name__ == "__main__":
    main()
