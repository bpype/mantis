import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple



@dataclass
class PassRecord:
    pass_name: str
    durations: List[float] = field(default_factory=list)

    def add_duration(self, duration: float):
        self.durations.append(duration)

    def stats(self):
        if not self.durations:
            return {"count": 0, "avg": 0, "total": 0, "max": 0, "min": 0}
        return {
            "count": len(self.durations),
            "avg": sum(self.durations) / len(self.durations),
            "total": sum(self.durations),
            "max": max(self.durations),
            "min": min(self.durations),
        }


@dataclass
class NodeRecord:
    node_type: str
    node_id: Tuple[Optional[str]] = field(default_factory=tuple)
    passes: Dict[str, PassRecord] = field(default_factory=dict)

    def record_pass(self, pass_name: str, duration: float):
        if pass_name not in self.passes:
            self.passes[pass_name] = PassRecord(pass_name)
        self.passes[pass_name].add_duration(duration)

    def stats(self):
        return {pname: prec.stats() for pname, prec in self.passes.items()}


@dataclass
class ProfileSession:
    name: str
    nodes: Dict[Tuple[Optional[str]], NodeRecord] = field(default_factory=dict)

    def record(self, node_id: Tuple[Optional[str]], node_type: str, pass_name: str, duration: float):
        if node_id not in self.nodes:
            self.nodes[node_id] = NodeRecord(node_id, node_type)
        self.nodes[node_id].record_pass(pass_name, duration)

    def stats(self):
        return {nid: node.stats() for nid, node in self.nodes.items()}


class NodeProfiler:
    def __init__(self):
        self.sessions: Dict[str, ProfileSession] = {}

    def new_session(self, name: str):
        self.sessions[name] = ProfileSession(name)
        self._current = self.sessions[name]

    def record(self, node, pass_name, *args, **kwargs):
        """Profile execution of a function (e.g., node pass)."""
        node_id = node.signature
        node_type = node.__class__.__name__
        func = getattr(node, pass_name)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        self._current.record(node_type, node_id, pass_name, duration)
        return result

    def get_stats(self, session_name: Optional[str]):
        if session_name is None:
            session_name = list(self.sessions.keys())[-1] # get the lastest one
        return self.sessions[session_name].stats()

    def to_json(self):
        def encode(obj):
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            return obj
        return json.dumps(self.sessions, default=encode, indent=2)

    @classmethod
    def from_json(cls, data: str):
        raw = json.loads(data)
        profiler = cls()
        for sname, sdata in raw.items():
            session = ProfileSession(name=sdata["name"])
            for nid, ndata in sdata["nodes"].items():
                node = NodeRecord(node_id=ndata["node_id"], node_type=ndata["node_type"])
                for pname, pdata in ndata["passes"].items():
                    record = PassRecord(pname, pdata["durations"])
                    node.passes[pname] = record
                session.nodes[nid] = node
            profiler.sessions[sname] = session
        return profiler


def summarize_profile(session, pass_name = "", sort_key='total'):
    """
    Print a formatted summary from a ProfileSession object.
    Columns: Node Type | Count | Total | Average | Min | Max
    """
    from ..base_definitions import FLOAT_EPSILON
    from collections import defaultdict

    summary = defaultdict(lambda: {"count": 0, "total": 0.0, "min": float("inf"), "max": 0.0})

    for node in session.nodes.values():
        node_type = node.node_type
        prec = node.passes.get(pass_name)
        if prec: # not every node does every pass.
            for d in prec.durations:
                s = summary[node_type]
                s["count"] += 1
                s["total"] += d
                s["min"] = min(s["min"], d)
                s["max"] = max(s["max"], d)

    # Prepare and print the table
    print(f"Pass: {pass_name}\n")
    header =  f"{'Node Type':<40}{'Count':>8}{'Total(s)':>12}{'Avg(s)':>12}{'Min(s)':>12}{'Max(s)':>12}"
    print(header)
    print("-" * len(header))

    sorted_items = list(summary.items())
    sorted_items.sort(key = lambda a : -a[1][sort_key]) # for some reason this reverse sorts if I don't negate it?

    accumulated_count = 0; accumulated_total = 0; overall_avg = 0
    overall_min = float("inf"); overall_max = -1

    for node_type, data in sorted_items:
        count = data["count"]; total = data["total"]
        accumulated_total += total # always accumulate this even for noop
        avg = total / count if count else 0
        if avg < 0.0000033: continue # try to avoid printing it if it is a no-op or not significant
        accumulated_count += count
        overall_min = min(overall_min, data['min']); overall_max = max(overall_max, data['max'])
        print(f"{node_type:<40}{count:>8}{total:>12.4f}{avg:>12.4f}{data['min']:>12.4f}{data['max']:>12.4f}")
    
    if accumulated_count != 0: # avoid zero-division. The average is not meaningful in this case, anyway.
        overall_avg = accumulated_total/accumulated_count

    footer =  f"{f'Summary({pass_name}): ':<40}{int(accumulated_count):>8}{accumulated_total:>12.4f}{overall_avg:>12.4f}{overall_min:>12.4f}{overall_max:>12.4f}"
    print("-" * len(footer))
    print(footer)
    print ("\n")