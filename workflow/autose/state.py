"""Run context shared by stages: the work directory, budgets and totals."""
import json
import time
from dataclasses import dataclass, field


@dataclass
class Ctx:
    issue_no: int
    issue_title: str
    issue_text: str
    round_no: int
    workdir: str
    base_sha: str
    branch: str
    runs: object
    local: bool = False
    findings: str = ""                # review findings from the previous round, if any
    counters: dict = field(default_factory=dict)
    tokens: int = 0
    calls: int = 0
    tiers: list = field(default_factory=list)
    log_lines: list = field(default_factory=list)
    cur_stage: str = ""

    def log(self, msg):
        line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
        self.log_lines.append(line)
        print(line, flush=True)

    def bump(self, key):
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    def snapshot(self, stage, status, reason=""):
        st = self.runs.state()
        st.update({"issue": self.issue_no, "round": self.round_no, "stage": stage,
                   "status": status, "reason": reason, "counters": self.counters,
                   "tokens": st.get("tokens_total", 0), "branch": self.branch,
                   "base_sha": self.base_sha, "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        st["tokens_total"] = st.get("tokens_total", 0)
        rounds = st.setdefault("rounds", {})
        rounds[str(self.round_no)] = {"tokens": self.tokens, "calls": self.calls,
                                      "models": sorted(set(self.tiers)), "stage": stage,
                                      "status": status, "reason": reason}
        st["tokens_total"] = sum(r["tokens"] for r in rounds.values())
        self.runs.save_state(st)


def _persist(self):
    self.runs.persist("autose: issue %s round %s" % (self.issue_no, self.round_no), remote=not self.local)


Ctx.persist = _persist
