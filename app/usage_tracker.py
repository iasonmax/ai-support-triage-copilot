# usage_tracker.py
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict


@staticmethod
def _default_article_stats() -> dict:
    """Default stats for a KB article"""
    return {
        "total_times_suggested": 0,
        "times_marked_helpful": 0,
        "times_failed": 0,
        "times_partially_helped": 0,
        "last_used": None,
    }


class UsageTracker:
    """Tracks KB article usage statistics"""
    
    def __init__(self, stats_file: str = "kb_usage_stats.json"):
        self.stats_file = Path(stats_file)
        self.stats = self._load_stats()
    
    def _load_stats(self) -> dict:
        """Load stats from file, or create empty"""
        if not self.stats_file.exists():
            return {}
        
        try:
            with open(self.stats_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_stats(self) -> None:
        """Save stats to file"""
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)
    
    def record_suggestion(self, kb_article_id: str) -> None:
        """
        Record that a KB article was suggested to a user.
        
        Args:
            kb_article_id: ID of the KB article
        """
        if kb_article_id not in self.stats:
            self.stats[kb_article_id] = _default_article_stats()
        
        self.stats[kb_article_id]["total_times_suggested"] += 1
        self.stats[kb_article_id]["last_used"] = datetime.utcnow().isoformat()
        self._save_stats()
    
    def record_outcome(
        self,
        kb_article_id: str,
        outcome: str,  # "helpful", "failed", "partial"
    ) -> None:
        """
        Record the outcome of a KB article suggestion.
        
        Args:
            kb_article_id: ID of the KB article
            outcome: "helpful", "failed", or "partial"
        """
        if kb_article_id not in self.stats:
            self.stats[kb_article_id] = _default_article_stats()
        
        if outcome == "helpful":
            self.stats[kb_article_id]["times_marked_helpful"] += 1
        elif outcome == "failed":
            self.stats[kb_article_id]["times_failed"] += 1
        elif outcome == "partial":
            self.stats[kb_article_id]["times_partially_helped"] += 1
        
        self.stats[kb_article_id]["last_used"] = datetime.utcnow().isoformat()
        self._save_stats()
    
    def get_stats(self, kb_article_id: str) -> dict:
        """
        Get stats for a KB article.
        
        Args:
            kb_article_id: ID of the KB article
            
        Returns:
            dict: Stats including success_rate
        """
        if kb_article_id not in self.stats:
            return {
                **_default_article_stats(),
                "success_rate": 0.0,
            }
        
        stats = self.stats[kb_article_id].copy()
        
        # Calculate success rate
        total = stats["times_marked_helpful"] + stats["times_failed"] + stats["times_partially_helped"]
        if total > 0:
            stats["success_rate"] = stats["times_marked_helpful"] / total
        else:
            stats["success_rate"] = 0.0
        
        return stats
    
    def get_all_stats(self) -> dict:
        """Get all tracked stats"""
        result = {}
        for article_id in self.stats.keys():
            result[article_id] = self.get_stats(article_id)
        return result
    
    def get_articles_needing_attention(
        self,
        success_rate_threshold: float = 0.5,
    ) -> list:
        """
        Get articles with low success rates (need improvement).
        
        Args:
            success_rate_threshold: Articles below this rate flagged
            
        Returns:
            list: Article IDs with low success rates
        """
        articles = []
        for article_id in self.stats.keys():
            stats = self.get_stats(article_id)
            # Only flag if suggested at least 3 times
            if (stats["total_times_suggested"] >= 3 and
                stats["success_rate"] < success_rate_threshold):
                articles.append({
                    "article_id": article_id,
                    "success_rate": stats["success_rate"],
                    "total_suggestions": stats["total_times_suggested"],
                })
        
        return sorted(articles, key=lambda x: x["success_rate"])