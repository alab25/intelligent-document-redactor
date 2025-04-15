import argparse
import glob
import os
import re
import sys
from pathlib import Path
import fitz  # PyMuPDF
import spacy
#import neuralcoref
import requests
from tqdm import tqdm
#from spacy.language import Language
#import en_coreference_web_trf
from spacy.lang.en import English
from transformers import pipeline

from fastcoref import FCoref
from fastcoref import spacy_component


def parse_arguments(args=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", 
        nargs="+", 
        help="input files globs"
    )
    parser.add_argument(
        "--output", 
        help="output directory for pdf files"
    )
    parser.add_argument(
        "--names", 
        action="append", 
        help="Takes one or more case sensitive tokens as input"
    )
    parser.add_argument(
        "--entities", 
        action="store_true", 
        help="Get all `named` entities"
    )
    parser.add_argument(
        "--coref", 
        action="store_true", 
        help="Redact all coreferences"
    )
    parser.add_argument(
        "--stats", 
        help="Specify the location of the stats file", 
        default=None
    )
    return parser.parse_args(args)

def load_nlp_models_2():
    """
    COREF = en_coreference_web_trf.load()
    # COREF = spacy.load("en_coreference_web_trf")
    COREF.disable_pipes("span_resolver", "span_cleaner")
    CORE = spacy.load("en_core_web_trf")

    nlp2= spacy.blank("en")

    for pipe in CORE.pipe_names:
        if pipe not in nlp2.pipe_names:
            nlp2.add_pipe(pipe, source=CORE)

    for pipe in COREF.pipe_names:
        if pipe not in nlp2.pipe_names:
            nlp2.add_pipe(pipe, source=COREF)
    
    return nlp2
    """
    pass



def load_nlp_models():
    """Load required NLP models."""
    print("Loading NLP models...")
    nlp = spacy.load("en_core_web_trf")
    print("Loaded en_core_web_trf model")
    
    return nlp

def get_input_files(input_globs):
    """Expand globs to get all input files."""
    all_files = []
    for pattern in input_globs:
        files = glob.glob(pattern)
        all_files.extend(files)
    return all_files

def get_coreference_mapping(text, nlp):
    # Process the text
    doc = nlp(text)
    
    # Initialize mapping list
    coref_pairs = []
    
    # Extract coreferences
    if doc._.coref_chains:
        for chain in doc._.coref_chains:
            # Get the main/original mention
            if len(chain) > 0:
                # Find the head/original mention (typically the first one)
                original_mention = chain.mentions[0]
                original_text = original_mention.pretty_representation
                original_idx = original_mention.root.i
                
                # Map all other mentions to this original
                for mention in chain.mentions[1:]:
                    mention_text = mention.pretty_representation
                    mention_idx = mention.root.i
                    
                    # Add to mapping
                    coref_pairs.append({str(mention_idx): mention_text, str(original_idx): original_text})
    
    # Return in the specified format
    return {"coreference_mapping": coref_pairs}


def redact_pdf(
    input_path, 
    output_path, 
    names_to_redact=None, 
    redact_entities=False, 
    redact_coref=False, 
    nlp=None,
    stats_data=None
):

    """Redact sensitive information from PDF."""
    if names_to_redact is None:
        names_to_redact = []
    
    if stats_data is None:
        stats_data = []
    
    # Open the PDF
    pdf_doc = fitz.open(input_path)
    
    # Process each page
    for page_num, page in enumerate(pdf_doc):
        # Get text from the page
        text = page.get_text()
        
        # Process with spaCy
        if nlp:
            doc_nlp = nlp(text)


            if len(names_to_redact)>0:
                expanded_names=[]
                for name in names_to_redact:
                    # Add original name
                    expanded_names.append(name)
                    
                    # Add case variations
                    expanded_names.append(name.lower())
                    expanded_names.append(name.upper())
                    expanded_names.append(name.title())
                    
                    # For names with spaces, add individual parts
                    if ' ' in name:
                        parts = name.split()
                        for part in parts:
                            expanded_names.append(part)
                            expanded_names.append(part.lower())
                            expanded_names.append(part.upper())
                            expanded_names.append(part.title())
                print("EXPANDED NAMES LIST -- > ",expanded_names)
                for name in expanded_names:
                    instances = page.search_for(name)
                    if instances:
                        for inst in instances:
                            page.add_redact_annot(inst, fill=(0, 0, 0))
                            
                            # Track stats
                            stats_data.append((
                                os.path.basename(input_path),
                                f"{page_num}x{inst}",
                                name,
                                len(name),
                                "Name"
                            ))

            if len(names_to_redact)>0:
                print(names_to_redact)

                for name in names_to_redact:
                    # Create regex pattern for case-insensitive matching with flexible whitespace
                    pattern = r'\b' + re.sub(r'\s+', r'\\s+', re.escape(name)) + r'\b'
                    
                    # Use regex search to find all instances with case insensitivity
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        matched_text = match.group()
                        instances = page.search_for(matched_text)

                        if instances:
                            for inst in instances:
                                page.add_redact_annot(inst, fill=(0, 0, 0))
                                
                                # Track stats
                                stats_data.append((
                                    os.path.basename(input_path),
                                    f"{page_num}x{inst}",
                                    name,
                                    len(name),
                                    "Name"
                                ))

            
            # Process entities if requested
            if redact_entities:
                for ent in doc_nlp.ents:
                    if ent.label_ == "PERSON":
                        # Track stats
                        stats_data.append((
                            os.path.basename(input_path),
                            f"{page_num}x{page.search_for(ent.text)}", 
                            ent.text, 
                            len(ent.text), 
                            ent.label_
                        ))
                        
                        # Find all instances on the page
                        instances = page.search_for(ent.text)
                        for inst in instances:
                            page.add_redact_annot(inst, fill=(0, 0, 0))
            
                
            # Process coreferences if requested
            if redact_coref:
                
                if "fastcoref" not in nlp.pipe_names:
                    nlp.add_pipe("fastcoref", config={'model_architecture': 'LingMessCoref', 'model_path': 'biu-nlp/lingmess-coref', 'device': 'cpu'})

                doc=nlp(text)

                print('doc object from nlp(text) inside the redact_coref: part of code PAGE_NUM---',page_num)
                print('PRINTING EACH ITEM inside page')
                for each in doc:
                    print("$$$$")
                    print('each',each)
                    print("***")
                print('PRINTING EACH ITEM inside page')



                clusters=doc._.coref_clusters
                coref_mapping=dict()
                coref_mapping["coreference_mapping"]=clusters
                

                # Create a list of span indices that should be redacted
                spans_to_redact = []
                
                
                # Get all words on the page with their positions
                words_info = page.get_text("words")
                
                # Extract the text from the page to find the actual entity words
                page_text = page.get_text()

                # For each cluster
                for cluster in clusters:
                    # First determine if this cluster should be redacted
                    should_redact = False
                    cluster_words = []
                    
                    # Collect all words in this cluster
                    for start_idx, end_idx in cluster:
                        for word_idx in range(start_idx, end_idx):
                            if word_idx < len(words_info):
                                word = words_info[word_idx][4]  # Get the actual word
                                cluster_words.append(word)
                    
                    # Check if any word in the cluster is in names_to_redact
                    for word in cluster_words:
                        if word in expanded_names:
                            should_redact = True
                            break
                    
                    # If we should redact this cluster, add all its word indices
                    if should_redact:
                        for start_idx, end_idx in cluster:
                            for word_idx in range(start_idx, end_idx):
                                if word_idx < len(words_info):
                                    word = words_info[word_idx][4]
                                    spans_to_redact.append((word_idx, word))

                # Sort spans to redact by position index
                spans_to_redact.sort()

                # Now redact each word
                for position_index, entity in spans_to_redact:
                    # Create a rect for this entity
                    rect = fitz.Rect(words_info[position_index][0], words_info[position_index][1], 
                                    words_info[position_index][2], words_info[position_index][3])

                    # Add redaction annotation
                    page.add_redact_annot(rect, fill=(0, 0, 0))

                    # Track stats
                    stats_data.append((
                        os.path.basename(input_path),
                        f"{page_num}x{position_index}",
                        entity,
                        len(entity),
                        "Coref"
                    ))
        
        # Apply redactions
        page.apply_redactions()
    
    # Save the redacted PDF
    pdf_doc.save(output_path)
    pdf_doc.close()
    
    return stats_data

def write_stats(stats_data, stats_file=None):
    """Write statistics to file or stderr."""
    output = stats_file if stats_file else sys.stderr
    
    if stats_file:
        with open(stats_file, 'w', encoding='utf-8' ) as f:
            for item in stats_data:
                f.write('\t'.join(map(str, item)) + '\n')
    else:
        for item in stats_data:
            print('\t'.join(map(str, item)), file=output)

def main():
    """Main function to execute the redaction system."""
    args = parse_arguments()
    
    # Validate arguments
    if not args.input:
        print("Error: --input is required", file=sys.stderr)
        return 1
    
    if not args.output:
        print("Error: --output is required", file=sys.stderr)
        return 1
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Get input files
    input_files = get_input_files(args.input)
    if not input_files:
        print(f"No files found matching patterns: {args.input}", file=sys.stderr)
        return 1
    
    # Load NLP model if needed
    nlp = None
    if args.entities or args.coref or args.names:
        nlp = load_nlp_models()
    
    # Process each file
    stats_data = []
    for input_file in tqdm(input_files, desc="Processing files"):
        # Determine output path
        output_file = os.path.join(args.output, os.path.basename(input_file))
        
        # Redact the file
        file_stats = redact_pdf(
            input_file,
            output_file,
            names_to_redact=args.names,
            redact_entities=args.entities,
            redact_coref=args.coref,
            nlp=nlp,
            stats_data=stats_data
        )
        
        print(f"Processed {input_file} -> {output_file}")
    
    # Write statistics
    write_stats(stats_data, args.stats)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
