import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main
from main import parse_arguments

def test_parse_arguments():
    args = parse_arguments(["--input", "file1.pdf", "--output", "output_dir"])
    
    assert args.input == ["file1.pdf"]
    assert args.output == "output_dir"
    assert args.names is None
    assert not args.entities
    assert not args.coref
    assert args.stats is None
    print("all test cases passed")

def test_parse_arguments_direct_with_all_options():
    """Test parsing all available arguments directly."""
    args = parse_arguments([
        "--input", "file1.pdf", "file2.pdf",
        "--output", "output_dir",
        "--names", "John Doe", 
        "--names", "Jane Smith",
        "--entities",
        "--coref",
        "--stats", "stats_file.txt"
    ])
    
    assert args.input == ["file1.pdf", "file2.pdf"]
    assert args.output == "output_dir"
    assert args.names == ["John Doe", "Jane Smith"]
    assert args.entities is True
    assert args.coref is True
    assert args.stats == "stats_file.txt"
    print("all test cases passed")

if __name__=='__main__':
    test_parse_arguments()
    test_parse_arguments_direct_with_all_options()
