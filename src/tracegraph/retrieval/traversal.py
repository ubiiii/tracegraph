"""Graph traversal retriever."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

import networkx as nx

from tracegraph.data.models import Chunk, RetrievedNode, TraversalPath
from tracegraph.retrieval.scoring import combined_traversal_score


def format_edge_hop(edge_data: dict) -> str:
    """Human-readable label for one graph edge (entities for SHARED_ENTITY, etc.)."""
    et = str(edge_data.get("edge_type", "UNKNOWN"))
    meta = edge_data.get("metadata")
    if not isinstance(meta, dict):
        meta = {}
    if et == "SHARED_ENTITY":
        ents = meta.get("shared_entities") or []
        if ents:
            return f"SHARED_ENTITY ({', '.join(str(e) for e in ents)})"
        return "SHARED_ENTITY"
    if et == "LEXICAL_SIM":
        sim = meta.get("similarity")
        if sim is not None:
            return f"LEXICAL_SIM (similarity {float(sim):.2f})"
        return "LEXICAL_SIM"
    if et == "NEXT":
        return "NEXT (adjacent in document)"
    if et == "RELATION":
        r = meta.get("reason", "")
        return f"RELATION ({r})" if r else "RELATION"
    return et


@dataclass(order=True)
class FrontierState:
    """State for priority frontier traversal."""

    priority: float
    node_id: str = field(compare=False)
    start_seed: str = field(compare=False)
    depth: int = field(compare=False)
    path_nodes: list[str] = field(compare=False)
    edge_types: list[str] = field(compare=False)
    hop_descriptions: list[str] = field(compare=False)


class GraphTraversalRetriever:
    """Bounded priority traversal from seed nodes."""

    def traverse(self, query: str, seed_nodes: list[RetrievedNode], graph: nx.MultiDiGraph, config) -> list[RetrievedNode]:
        """Traverse graph from seeds and return ranked discovered nodes."""
        if not seed_nodes:
            return []
        selected: dict[str, RetrievedNode] = {s.node_id: s for s in seed_nodes if s.node_id in graph}
        frontier: list[FrontierState] = []
        for s in seed_nodes:
            if s.node_id in graph:
                heapq.heappush(
                    frontier,
                    FrontierState(
                        priority=-s.score,
                        node_id=s.node_id,
                        start_seed=s.node_id,
                        depth=0,
                        path_nodes=[s.node_id],
                        edge_types=[],
                        hop_descriptions=[],
                    ),
                )

        best_score = {s.node_id: s.score for s in seed_nodes}
        while frontier and len(selected) < config.traversal.max_nodes:
            state = heapq.heappop(frontier)
            if state.depth >= config.traversal.max_depth:
                continue
            neighbors = list(graph.out_edges(state.node_id, data=True, keys=True))
            local_candidates: list[tuple[float, RetrievedNode, list[str], list[str], list[str]]] = []
            selected_chunks = [r.chunk for r in selected.values()]
            for _, tgt, _, edge_data in neighbors:
                if tgt not in graph:
                    continue
                ndata = graph.nodes[tgt]
                chunk = Chunk.model_validate(ndata)
                br = combined_traversal_score(query, chunk, edge_data, state.depth + 1, selected_chunks, config)
                score = br["total"]
                if score <= best_score.get(tgt, -1e9):
                    continue
                best_score[tgt] = score
                hop_label = format_edge_hop(edge_data)
                path_nodes = state.path_nodes + [tgt]
                edge_types = state.edge_types + [edge_data.get("edge_type", "UNKNOWN")]
                hop_descriptions = state.hop_descriptions + [hop_label]
                local_candidates.append(
                    (
                        score,
                        RetrievedNode(
                            node_id=tgt,
                            score=score,
                            retrieval_stage="traversal",
                            traversal_score=score,
                            rank=0,
                            chunk=chunk,
                            score_breakdown={k: float(v) for k, v in br.items()},
                            path=TraversalPath(
                                start_node_id=state.start_seed,
                                end_node_id=tgt,
                                node_sequence=path_nodes,
                                edge_sequence=edge_types,
                                hop_descriptions=hop_descriptions,
                                cumulative_score=score,
                                depth=state.depth + 1,
                            ),
                            why_retrieved=f"Traversal from {state.node_id} via {edge_data.get('edge_type')}",
                        ),
                        path_nodes,
                        edge_types,
                        hop_descriptions,
                    )
                )
            local_candidates.sort(key=lambda x: (x[0], x[1].node_id), reverse=True)
            for score, result, p_nodes, e_types, hop_desc in local_candidates[: config.traversal.beam_width]:
                selected[result.node_id] = result
                heapq.heappush(
                    frontier,
                    FrontierState(
                        priority=-score,
                        node_id=result.node_id,
                        start_seed=state.start_seed,
                        depth=state.depth + 1,
                        path_nodes=p_nodes,
                        edge_types=e_types,
                        hop_descriptions=hop_desc,
                    ),
                )

        ranked = sorted(selected.values(), key=lambda r: (r.score, r.node_id), reverse=True)
        for i, r in enumerate(ranked, start=1):
            r.rank = i
        return ranked[: config.traversal.max_nodes]
