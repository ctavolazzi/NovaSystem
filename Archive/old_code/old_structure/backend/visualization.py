"""
NovaSystem Visualization Module

This module provides tools for visualizing the Nova Process flow,
including agent interactions and process stages.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import these if available in the environment
try:
    import matplotlib.pyplot as plt
    import networkx as nx
    from graphviz import Digraph
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    logging.warning("Visualization dependencies not installed. Run: pip install matplotlib networkx graphviz")

logger = logging.getLogger(__name__)

class NovaVisualizer:
    """
    Visualization tools for the Nova Process.

    This class generates visual representations of the Nova Process
    iterations, agent interactions, and process flow.
    """

    def __init__(self, output_dir: str = "visualizations"):
        """Initialize the visualizer."""
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.has_dependencies = VISUALIZATION_AVAILABLE

    def generate_process_graph(self, iteration_data: Dict[str, Any], filename: Optional[str] = None) -> bool:
        """
        Generate a graph visualization of the Nova Process flow.

        Args:
            iteration_data: Data from a completed Nova Process iteration.
            filename: Output filename (without extension). If None, a timestamped name is used.

        Returns:
            True if the visualization was created, False otherwise.
        """
        if not self.has_dependencies:
            logger.warning("Visualization dependencies not installed")
            return False

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            iteration_id = iteration_data.get("id", "unknown")
            filename = f"nova_process_{iteration_id}_{timestamp}"

        # Create a directed graph
        dot = Digraph(comment='Nova Process Flow')

        # Add the problem statement as the root node
        problem = iteration_data.get("problem_statement", "Unknown Problem")
        truncated_problem = problem[:50] + "..." if len(problem) > 50 else problem
        dot.node('problem', f"Problem:\n{truncated_problem}", shape='box', style='filled', fillcolor='lightblue')

        # Add nodes for each stage
        stages = iteration_data.get("stages", {})
        stage_nodes = {}

        # Define stage colors
        stage_colors = {
            "problem_unpacking": "lightgreen",
            "expertise_assembly": "lightyellow",
            "collaborative_ideation": "lightpink",
            "critical_analysis": "lightsalmon",
            "summary_and_next_steps": "lightcyan"
        }

        # Add stage nodes
        for stage_name in stage_colors:
            node_id = f"stage_{stage_name}"
            display_name = stage_name.replace('_', ' ').title()
            color = stage_colors.get(stage_name, "white")

            if stage_name in stages:
                dot.node(node_id, display_name, shape='box', style='filled', fillcolor=color)
                stage_nodes[stage_name] = node_id

        # Connect the stages in sequence
        dot.edge('problem', 'stage_problem_unpacking')
        if 'problem_unpacking' in stages and 'expertise_assembly' in stages:
            dot.edge('stage_problem_unpacking', 'stage_expertise_assembly')
        if 'expertise_assembly' in stages and 'collaborative_ideation' in stages:
            dot.edge('stage_expertise_assembly', 'stage_collaborative_ideation')
        if 'collaborative_ideation' in stages and 'critical_analysis' in stages:
            dot.edge('stage_collaborative_ideation', 'stage_critical_analysis')
        if 'critical_analysis' in stages and 'summary_and_next_steps' in stages:
            dot.edge('stage_critical_analysis', 'stage_summary_and_next_steps')

        # Add expert nodes if present
        experts = iteration_data.get("required_experts", [])
        expert_nodes = {}

        for expert in experts:
            node_id = f"expert_{expert.replace(' ', '_').lower()}"
            dot.node(node_id, f"{expert}", shape='ellipse', style='filled', fillcolor='lightskyblue')
            expert_nodes[expert] = node_id

            # Connect each expert to the collaborative ideation stage
            if 'collaborative_ideation' in stage_nodes:
                dot.edge(expert_nodes[expert], stage_nodes['collaborative_ideation'])

        # Connect expertise assembly to experts
        if experts and 'expertise_assembly' in stage_nodes:
            for expert in experts:
                dot.edge(stage_nodes['expertise_assembly'], expert_nodes[expert])

        # Add summary and next steps if complete
        if iteration_data.get("complete", False):
            summary = iteration_data.get("summary", "No summary available")
            truncated_summary = summary[:50] + "..." if len(summary) > 50 else summary

            next_steps = iteration_data.get("next_steps", "No next steps available")
            truncated_next_steps = next_steps[:50] + "..." if len(next_steps) > 50 else next_steps

            # Add summary node
            dot.node('summary', f"Summary:\n{truncated_summary}", shape='box', style='filled', fillcolor='palegreen')
            dot.edge('stage_summary_and_next_steps', 'summary')

            # Add next steps node
            dot.node('next_steps', f"Next Steps:\n{truncated_next_steps}", shape='box', style='filled', fillcolor='paleturquoise')
            dot.edge('summary', 'next_steps')

        # Save the graph
        output_path = os.path.join(self.output_dir, filename)
        dot.render(output_path, format='png', cleanup=True)
        logger.info(f"Visualization saved to: {output_path}.png")

        return True

    def generate_agent_interaction_graph(self, iteration_data: Dict[str, Any], filename: Optional[str] = None) -> bool:
        """
        Generate a graph visualization of agent interactions.

        Args:
            iteration_data: Data from a completed Nova Process iteration.
            filename: Output filename (without extension). If None, a timestamped name is used.

        Returns:
            True if the visualization was created, False otherwise.
        """
        if not self.has_dependencies:
            logger.warning("Visualization dependencies not installed")
            return False

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            iteration_id = iteration_data.get("id", "unknown")
            filename = f"agent_interactions_{iteration_id}_{timestamp}"

        # Create a network graph
        G = nx.Graph()

        # Add DCE node
        G.add_node("DCE", type="agent", size=2000, color='blue')

        # Add CAE node if critical analysis was performed
        if iteration_data.get("critical_analysis"):
            G.add_node("CAE", type="agent", size=2000, color='red')
            G.add_edge("DCE", "CAE", weight=2)

        # Add expert nodes
        experts = iteration_data.get("required_experts", [])
        for expert in experts:
            G.add_node(expert, type="expert", size=1500, color='green')
            G.add_edge("DCE", expert, weight=1)

            if "CAE" in G.nodes:
                G.add_edge("CAE", expert, weight=1, style='dashed')

        # Create the visualization
        plt.figure(figsize=(12, 8))

        # Define node positions using spring layout
        pos = nx.spring_layout(G, seed=42)

        # Get node attributes for drawing
        node_colors = [G.nodes[n].get('color', 'gray') for n in G.nodes]
        node_sizes = [G.nodes[n].get('size', 1000) for n in G.nodes]

        # Draw the graph
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
        nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')

        plt.axis('off')
        plt.title('Nova Process Agent Interactions')

        # Save the figure
        output_path = os.path.join(self.output_dir, filename + '.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Agent interaction graph saved to: {output_path}")
        return True


def save_iteration_json(iteration_data: Dict[str, Any], output_dir: str = "visualizations") -> str:
    """
    Save iteration data as a JSON file for later analysis.

    Args:
        iteration_data: Data from a Nova Process iteration.
        output_dir: Directory to save the JSON file.

    Returns:
        Path to the saved JSON file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    iteration_id = iteration_data.get("id", "unknown")
    filename = f"nova_iteration_{iteration_id}_{timestamp}.json"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, 'w') as f:
        json.dump(iteration_data, f, indent=2)

    logger.info(f"Iteration data saved to: {output_path}")
    return output_path