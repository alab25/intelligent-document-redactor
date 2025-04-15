import sys
import os
import requests
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main
from main import redact_pdf

def test_redact_pdf():

    # Setup paths as before
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_pattern = os.path.join(project_root, "resources", "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    input_path = pdf_files[0]
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_root, "resources", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a full file path for the output PDF
    output_file = os.path.join(output_dir, "redacted_" + os.path.basename(input_path))
    
    # Path for stats file
    stats_path = os.path.join(project_root, "resources", "stats.txt")
    
    


    print(f"Using input path: {input_path}")
    print(f"Using output path: {output_file}")
    print(f"Using stats path: {stats_path}")


    output=redact_pdf(input_path, output_file, names_to_redact=["Flavius","Cassius","José Bonilla"], stats_data=stats_path)
    assert output is not None
    print("all test cases passed.")

def test_redact_pdf_entities():
    # Setup paths as before
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_pattern = os.path.join(project_root, "resources", "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    input_path = pdf_files[0]
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_root, "resources", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a full file path for the output PDF
    output_file = os.path.join(output_dir, "redacted_" + os.path.basename(input_path))
    
    # Path for stats file
    stats_path = os.path.join(project_root, "resources", "stats.txt")
    
    


    print(f"Using input path: {input_path}")
    print(f"Using output path: {output_file}")
    print(f"Using stats path: {stats_path}")


    output=redact_pdf(input_path, output_file, names_to_redact=["Flavius","Cassius","José Bonilla"], redact_entities=True,stats_data=stats_path)
    assert output is not None
    print("all test cases passed.")

def test_redact_pdf_coref():
    # Setup paths as before
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_pattern = os.path.join(project_root, "resources", "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    input_path = pdf_files[0]
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_root, "resources", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a full file path for the output PDF
    output_file = os.path.join(output_dir, "redacted_" + os.path.basename(input_path))
    
    # Path for stats file
    stats_path = os.path.join(project_root, "resources", "stats.txt")
    
    


    print(f"Using input path: {input_path}")
    print(f"Using output path: {output_file}")
    print(f"Using stats path: {stats_path}")


    output=redact_pdf(input_path, output_file, names_to_redact=["Flavius","Cassius","José Bonilla"], redact_coref=True,stats_data=stats_path)
    assert output is not None
    print("all test cases passed.")



if __name__=='__main__':
    test_redact_pdf()
    test_redact_pdf_entities()
    test_redact_pdf_coref()


