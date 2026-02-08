"""Test result persistence and retrieval.

This module provides functionality for storing and retrieving test results
from Hardware-in-the-Loop (HIL) simulations. It includes the ResultStorage class
for managing result files, campaign summaries, and aggregate statistics.

Classes:
    ResultStorage: Handles saving, loading, and managing test result data.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class ResultStorage:
    """Manages persistent storage and retrieval of test results.

    This class provides methods to save individual scenario results, retrieve
    results for specific scenarios or campaigns, and compute aggregate statistics.
    Results are stored as JSON files in a specified directory.

    Attributes:
        results_dir (Path): Directory where result files are stored.
    """

    def __init__(self, results_dir: str = "astraguard/hil/results"):
        """Initialize result storage.

        Args:
            results_dir (str): Directory for result files.
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def save_scenario_result(
        self, scenario_name: str, result: Dict[str, Any]
    ) -> str:
        """Save individual scenario result to file asynchronously.

        Args:
            scenario_name (str): Name of scenario (without .yaml).
            result (Dict[str, Any]): Execution result dict.

        Returns:
            str: Path to saved result file.

        Raises:
            OSError: If there is an issue writing to the file.
            ValueError: If the result dict contains non-serializable data.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{scenario_name}_{timestamp}.json"
        filepath = self.results_dir / filename

        # Ensure result has metadata
        result_with_metadata = {
            "scenario_name": scenario_name,
            "timestamp": datetime.now().isoformat(),
            **result,
        }

        # Use asyncio.to_thread for I/O operations
        await asyncio.to_thread(filepath.write_text, json.dumps(result_with_metadata, indent=2, default=str))
        return str(filepath)

    async def get_scenario_results(
        self, scenario_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve recent results for a specific scenario asynchronously.

        Args:
            scenario_name (str): Name of scenario.
            limit (int, optional): Maximum results to return. Defaults to 10.

        Returns:
            List[Dict[str, Any]]: List of result dicts (newest first).

        Raises:
            OSError: If there is an issue reading result files.
            json.JSONDecodeError: If a result file contains invalid JSON.
        """
        pattern = f"{scenario_name}_*.json"
        result_files = sorted(self.results_dir.glob(pattern), reverse=True)[:limit]

        async def load_result(result_file):
            try:
                return await asyncio.to_thread(json.loads, result_file.read_text())
            except Exception as e:
                print(f"[WARN] Failed to load result {result_file.name}: {e}")
                return None

        results = await asyncio.gather(*[load_result(f) for f in result_files])
        return [r for r in results if r is not None]

    async def get_recent_campaigns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent campaign summaries asynchronously.

        Args:
            limit (int, optional): Maximum campaigns to return. Defaults to 10.

        Returns:
            List[Dict[str, Any]]: List of campaign summary dicts (newest first).

        Raises:
            OSError: If there is an issue reading campaign files.
            json.JSONDecodeError: If a campaign file contains invalid JSON.
        """
        campaign_files = sorted(
            self.results_dir.glob("campaign_*.json"), reverse=True
        )[:limit]

        async def load_campaign(campaign_file):
            try:
                return await asyncio.to_thread(json.loads, campaign_file.read_text())
            except Exception as e:
                print(f"[WARN] Failed to load campaign {campaign_file.name}: {e}")
                return None

        campaigns = await asyncio.gather(*[load_campaign(f) for f in campaign_files])
        return [c for c in campaigns if c is not None]

    async def get_campaign_summary(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific campaign by ID asynchronously.

        Args:
            campaign_id (str): Campaign timestamp ID (YYYYMMDD_HHMMSS).

        Returns:
            Optional[Dict[str, Any]]: Campaign summary dict or None if not found.

        Raises:
            OSError: If there is an issue reading the campaign file.
            json.JSONDecodeError: If the campaign file contains invalid JSON.
        """
        campaign_file = self.results_dir / f"campaign_{campaign_id}.json"
        if not await asyncio.to_thread(campaign_file.exists):
            return None

        try:
            return await asyncio.to_thread(json.loads, campaign_file.read_text())
        except Exception as e:
            print(f"[ERROR] Failed to load campaign {campaign_id}: {e}")
            return None

    async def get_result_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics across all results asynchronously.

        Returns:
            Dict[str, Any]: Dict with statistics including total_campaigns,
                total_scenarios, total_passed, and avg_pass_rate.
        """
        campaigns = await self.get_recent_campaigns(limit=999)
        if not campaigns:
            return {
                "total_campaigns": 0,
                "total_scenarios": 0,
                "avg_pass_rate": 0.0,
            }

        total_campaigns = len(campaigns)
        total_scenarios = sum(c.get("total_scenarios", 0) for c in campaigns)
        total_passed = sum(c.get("passed", 0) for c in campaigns)
        avg_pass_rate = total_passed / total_scenarios if total_scenarios > 0 else 0.0

        return {
            "total_campaigns": total_campaigns,
            "total_scenarios": total_scenarios,
            "total_passed": total_passed,
            "avg_pass_rate": avg_pass_rate,
        }

    async def clear_results(self, older_than_days: int = 30) -> int:
        """Remove old result files asynchronously.

        Args:
            older_than_days (int, optional): Delete files older than this many days. Defaults to 30.

        Returns:
            int: Number of files deleted.

        Raises:
            OSError: If there is an issue accessing or deleting files.
        """
        from time import time

        cutoff_time = time() - (older_than_days * 86400)
        deleted_count = 0

        async def check_and_delete(result_file):
            nonlocal deleted_count
            if await asyncio.to_thread(result_file.stat().st_mtime.__lt__, cutoff_time):
                await asyncio.to_thread(result_file.unlink)
                deleted_count += 1

        tasks = [check_and_delete(f) for f in self.results_dir.glob("*.json")]
        await asyncio.gather(*tasks)

        return deleted_count
