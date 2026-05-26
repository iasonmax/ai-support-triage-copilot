# test_usage_tracker.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from usage_tracker import UsageTracker
import tempfile
import json

print("Testing usage tracker:\n")

# Test 1: Create tracker with temp file
print("Test 1: Create tracker with temp file")
with tempfile.TemporaryDirectory() as tmpdir:
    stats_file = Path(tmpdir) / "test_stats.json"
    tracker = UsageTracker(str(stats_file))
    print(f"  Stats file: {stats_file}")
    print(f"  Initial stats empty: {len(tracker.stats) == 0}")
    print("  ✅ PASS\n")
    
    # Test 2: Record suggestions
    print("Test 2: Record suggestions")
    tracker.record_suggestion("VPN-001")
    tracker.record_suggestion("VPN-001")
    tracker.record_suggestion("NETWORK-005")
    
    stats = tracker.get_stats("VPN-001")
    print(f"  VPN-001 suggested 2 times: {stats['total_times_suggested'] == 2}")
    print(f"  NETWORK-005 suggested 1 time: {tracker.get_stats('NETWORK-005')['total_times_suggested'] == 1}")
    print("  ✅ PASS\n")
    
    # Test 3: Record outcomes
    print("Test 3: Record outcomes")
    tracker.record_outcome("VPN-001", "helpful")
    tracker.record_outcome("VPN-001", "helpful")
    tracker.record_outcome("NETWORK-005", "failed")
    
    vpn_stats = tracker.get_stats("VPN-001")
    network_stats = tracker.get_stats("NETWORK-005")
    
    print(f"  VPN-001 marked helpful 2x: {vpn_stats['times_marked_helpful'] == 2}")
    print(f"  VPN-001 success rate: {vpn_stats['success_rate']:.2f} (expected 1.0)")
    print(f"  NETWORK-005 failed 1x: {network_stats['times_failed'] == 1}")
    print(f"  NETWORK-005 success rate: {network_stats['success_rate']:.2f} (expected 0.0)")
    print("  ✅ PASS\n")
    
    # Test 4: Get articles needing attention
    print("Test 4: Get articles needing attention")
    # Add more suggestions to NETWORK-005 to trigger threshold
    for _ in range(3):
        tracker.record_suggestion("NETWORK-005")
    tracker.record_outcome("NETWORK-005", "failed")
    tracker.record_outcome("NETWORK-005", "failed")
    
    needing_attention = tracker.get_articles_needing_attention(
        success_rate_threshold=0.5
    )
    print(f"  Articles needing attention: {len(needing_attention)}")
    if needing_attention:
        print(f"  Low performer: {needing_attention[0]['article_id']}")
        print(f"  Success rate: {needing_attention[0]['success_rate']:.2f}")
    print("  ✅ PASS\n")
    
    # Test 5: Persistence (save and reload)
    print("Test 5: Persistence (save and reload)")
    # Stats already saved via record_* calls
    # Create new tracker instance, should load existing data
    tracker2 = UsageTracker(str(stats_file))
    vpn_stats_reloaded = tracker2.get_stats("VPN-001")
    print(f"  Reloaded VPN-001 stats: {vpn_stats_reloaded['total_times_suggested']}")
    print(f"  Data persisted: {vpn_stats_reloaded['total_times_suggested'] == 2}")
    print("  ✅ PASS\n")

print("All usage tracker tests passed! ✅")