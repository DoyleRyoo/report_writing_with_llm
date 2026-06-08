from pydantic import BaseModel
from typing import List

class VulnerabilityReport(BaseModel):
  title: str
  severity: str
  vulnerability_type: str
  target: str
  description: str
  affected_parameter: str
  proof_of_concept: str
  impact: str
  remediation: List[str]