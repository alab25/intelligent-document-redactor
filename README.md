# cis6930sp25-project2
This project involves a robust project for redacting sensitive information from PDF documents using natural language processing and coreference resolution.
## Overview 
This PDF redaction project allows for intelligent redaction of:

- Specific named individuals
- All person entities automatically identified through NER
- Pronouns and references that refer to redacted entities (coreference resolution)
- The tool processes PDF files, identifies sensitive information according to specified criteria, and creates redacted versions with the sensitive information blacked out.

## How to run
1. Go inside DGX shell and use this apptainer (.def) file to create a .sif file.
### Contents of the .def file below : -
			
       Bootstrap: docker
	From: python:3.12
	
	%post
	
	    # Install system dependencies
	    apt-get update
	    apt-get install -y curl gcc git
	
	    # Install uv instead of pipenv
	    pip install uv
	
	    # Clone repository with hardcoded token
	    git clone https://alab25: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@github.com/alab25/cis6930sp25-project2.git /cis6930sp25-project2
	
	    # Change to the repository directory
	    cd /cis6930sp25-project2
	    
		# Create virtual environment in the project directory
		uv venv
	  
	    # Install dependencies - use system Python instead of virtual env for container simplicity
	    uv pip install --system -e .    
	
	    # Download spaCy model
	    python -m spacy download en_core_web_sm	
		python -m spacy download en_core_web_trf
	
	    # Make the main script executable
	    chmod +x main.py
		
	%environment
	    # Set the working directory in the PATH
	    export PATH=$PATH:/cis6930sp25-project2
	    export PYTHONPATH=$PYTHONPATH:/cis6930sp25-project2
		
	%runscript
	    # Run main.py from the repository directory
	    cd /cis6930sp25-project2
	    python main.py "$@"

2. Use this .def file to create a .sif file using command below : -
   apptainer build github_image19.sif github_image12.def

3. After .sif file is created, run the below command : -
   
   apptainer run --bind $(pwd)/resources/output:/cis6930sp25-project2/resources/output,$(pwd)/resources/stats.txt:/cis6930sp25-project2/resources/stats.txt 
   github_image19.sif --input "resources/*.pdf" --output "resources/output" --names "Flavius" --names "Cassius" --names "José Bonilla" --coref --stats 
   "resources/stats.txt"
   
   --bind is important since .sif does not automatically has access to local folders and its required to store the output.
   
5. You can check the output and stats file inside the resources/ouput folder.

## Functions Overview 
1.parse_arguments()
  Handles command-line argument parsing for the tool.
  
2.load_nlp_models() 
  Load the spaCy NLP models required for entity recognition and coreference resolution.
  
3.get_input_files(input_globs)
  Expands glob patterns to get a list of all input files.
  
4.redact_pdf(input_path, output_path, names_to_redact, redact_entities, redact_coref, nlp, stats_data)
  Core function that processes a PDF file, identifies entities for redaction based on parameters, and produces a redacted version.
  
5.write_stats(stats_data, stats_file)
  Writes statistics about redacted content to a file or standard error.
  
6.main()
  Orchestrates the overall redaction process based on command-line arguments.

## Images of code execution in DGX
![Screenshot (350)](https://github.com/user-attachments/assets/32d581c0-1b0c-445e-9ac7-6efd34c1aaf0)
![Screenshot (351)](https://github.com/user-attachments/assets/361a33b3-ce28-4b4c-ac81-1bf38aab2c4b)
![Screenshot (352)](https://github.com/user-attachments/assets/6240c446-f1e1-426c-abf9-b85c633a40be)




