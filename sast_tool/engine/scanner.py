import os
import asyncio
import logging
from typing import List
from sast_tool.engine.models import Finding, Severity
from sast_tool.rules.loader import RuleLoader
from sast_tool.sast.bandit_runner import BanditRunner
from sast_tool.sast.semgrep_runner import SemgrepRunner
from sast_tool.engine.aggregator import Aggregator
from sast_tool.ai.client import AIClient
from sast_tool.ai.cache import AICache  # Supporting the new caching layer

logger = logging.getLogger(__name__)

class Scanner:
    """
    Core scanning engine that orchestrates SAST tools and AI enrichment.
    Implements the 'Cost Guard' and 'Intelligence Layer' from the roadmap.
    """
    def __init__(self):
        self.rule_loader = RuleLoader()
        self.bandit = BanditRunner()
        self.semgrep = SemgrepRunner()
        self.aggregator = Aggregator()        
        self.ai_client = AIClient()
        self.ai_cache = AICache() # Initialize the SQLite cache
        
        # Define which severities deserve AI spend
        self.ai_severity_threshold = [Severity.HIGH, Severity.CRITICAL]

    async def scan_directory(self, directory_path: str) -> List[Finding]:
        """Performs a full scan on directories or single files and enriches findings."""
        logger.info(f"Starting scan for target: {directory_path}")
        all_findings = []
        rules = self.rule_loader.load_rules()

        # 1. Collect target files (Handles both single file path and full directory walks)
        target_files = []
        if os.path.isfile(directory_path):
            if directory_path.endswith(".py"):
                target_files.append(directory_path)
        else:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if file.endswith(".py"):
                        target_files.append(os.path.join(root, file))

        # 2. Run Internal Custom AST/Traverser Rules
        for file_path in target_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                    for rule in rules:
                        findings = rule.analyze(file_path, code)
                        all_findings.extend(findings)
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")

        # 3. Run Integrated Open-Source Tools (Only if a directory path is targeted)
        if os.path.isdir(directory_path):
            all_findings.extend(self.bandit.run(directory_path))
            all_findings.extend(self.semgrep.run(directory_path))

        # 4. Deduplicate and Aggregate
        unique_findings = self.aggregator.aggregate(all_findings)
        
        # 5. AI Enrichment with Cost Guards
        enriched_findings = await self._enrich_findings_parallel(unique_findings)

        return enriched_findings

    async def _enrich_findings_parallel(self, findings: List[Finding]) -> List[Finding]:
        """
        Enriches findings using batching and caching to fulfill Phase 1 requirements.
        """
        tasks = []
        for finding in findings:
            # Skip low-severity issues to save costs (Cost Guard)
            if finding.severity not in self.ai_severity_threshold:
                continue

            # Check cache first to avoid repeat API calls
            cached_fix = self.ai_cache.get(finding.rule_id, finding.snippet)
            if cached_fix:
                finding.ai_explanation = cached_fix.get("explanation")
                finding.recommended_fix = cached_fix.get("fix")
                continue

            # Create task for new AI enrichment
            tasks.append(self._process_single_ai_enrichment(finding))

        if tasks:
            logger.info(f"Enriching {len(tasks)} high-priority findings via AI...")
            await asyncio.gather(*tasks)

        return findings

    async def _process_single_ai_enrichment(self, finding: Finding):
        """Helper to call AI, parse response, and update cache."""
        enrichment_data = await self.ai_client.enrich_finding(finding, finding.snippet)
        
        if enrichment_data:
            finding.ai_explanation = enrichment_data.get("explanation")
            finding.recommended_fix = enrichment_data.get("fix")
            
            # Store in cache for future scans
            self.ai_cache.set(
                finding.rule_id, 
                finding.snippet, 
                enrichment_data
            )