import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main
from main import write_stats

def test_write_stats():
    
    # Sample stats data
    stats_data = [
        ("document1.pdf", "0x123", "John Smith", 10, "Name"),
        ("document2.pdf", "1x456", "Jane Doe", 8, "PERSON"),
        ("document3.pdf", "2x789", "he", 2, "Coref")
    ]

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    stats_path = os.path.join(project_root, "resources", "stats.txt")

    return_val=write_stats(stats_data,stats_path)
    assert return_val is True

if __name__=='__main__':
    test_write_stats() 