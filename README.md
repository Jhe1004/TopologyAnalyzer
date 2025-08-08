# TopologyAnalyzer

`TopologyAnalyzer` is a Python script designed for the batch analysis of phylogenetic tree topologies from a large number of gene trees. Its primary function is to quantify the phylogenetic relationship of one or more "Species of Interest" (SOI) relative to two distinct reference groups (Group A and Group B).

The script iterates through hundreds or thousands of Newick tree files, determines whether the SOI is more closely related to Group A or Group B in each tree, and aggregates these results into a clear summary table. A key feature is its use of a node support threshold (e.g., bootstrap values) to ensure that topological relationships are only counted if they are statistically well-supported.

It also includes a handy utility to automatically repair malformed Newick strings, making it robust to common formatting issues in tree files.

---

## Table of Contents
- [Key Features](#key-features)
- [How It Works (The Logic)](#how-it-works-the-logic)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Configuration](#configuration)
- [How to Run](#how-to-run)
- [Output Explanation](#output-explanation)
  - [Console Output](#console-output)
  - [CSV Output File](#csv-output-file)
  - [Fixed Trees Directory](#fixed-trees-directory)

---

## Key Features

-   **Batch Processing**: Efficiently analyzes hundreds or thousands of tree files in a single run.
-   **Automatic Tree Repair**: Automatically fixes common Newical format errors where internal nodes lack support values, preventing crashes and improving compatibility.
-   **Support-Based Validation**: Uses a configurable node support threshold (`SUPPORT_THRESHOLD`) to only consider relationships that are backed by strong statistical support.
-   **Topological Quantification**: For each Species of Interest (SOI), it tallies the number of trees that support a closer relationship to Group A versus Group B.
-   **Clear Summarized Output**: Generates a final CSV report that summarizes the counts for each tested relationship across all analyzed gene trees.
-   **Easy Configuration**: All parameters are set in a simple, well-commented configuration block at the top of the script. No command-line arguments are needed.

## How It Works (The Logic)

The script follows a clear and robust analytical workflow:

1.  **Find Trees**: It scans a specified directory for all files ending with a given suffix (e.g., `.tre`).
2.  **Repair Trees**: For each file found, it reads the Newick string and automatically repairs it by adding a default support value of `0` to any internal node that lacks one. The repaired tree is saved to a separate directory.
3.  **Analyze Topology**: For each repaired tree, the script performs the core analysis for every combination of `(SOI, species_A, species_B)`:
    a. It finds the Most Recent Common Ancestor (MRCA) of `(SOI, species_A)`, let's call it `MRCA_SA`.
    b. It finds the MRCA of `(SOI, species_B)`, let's call it `MRCA_SB`.
    c. It determines the relationship by checking if one MRCA is a descendant of the other. For example, if `MRCA_SB` is a descendant of `MRCA_SA`, it means the SOI shares a more recent ancestor with species_B than with species_A.
    d. It then checks the node support value of the more recent MRCA. Only if this value is **greater than** the `SUPPORT_THRESHOLD` is the relationship counted as "closer". Otherwise, it is marked as "undetermined".
4.  **Summarize Results**: After processing all trees, it aggregates the counts (`closer_to_A`, `closer_to_B`, `undetermined`) for every tested triplet and prints a summary to the console and a detailed CSV file.

## Dependencies

The script requires the `ete3` Python library.

## Installation

If you do not have `ete3` installed, you can install it via pip:

    pip install ete3

## Configuration

This script is configured by directly editing the variables in the **USER CONFIGURATION AREA** at the top of the `.py` file. There are no command-line arguments.

| Variable | Description |
|---|---|
| `TREE_DIR` | The path to the folder containing your Newick tree files. |
| `TREE_SUFFIX` | The file extension or suffix that identifies your tree files (e.g., `_cds` or `.tree`). |
| `SPECIES_A_LIST` | A Python list of strings, where each string is the exact name of a species in Group A as it appears in the tree files. |
| `SPECIES_B_LIST` | A Python list for the species names in Group B. |
| `SPECIES_OF_INTEREST`| A Python list for the species you want to analyze. |
| `SUPPORT_THRESHOLD` | An integer (0-100). A relationship is only considered valid if the relevant node's support is greater than this value. |
| `OUTPUT_CSV_FILE` | The name for the final summary CSV file that will be created. |
| `MODIFIED_TREE_DIR`| The name of a new directory that will be created to store the automatically repaired tree files. |

## How to Run

1.  **Place the script**: Put the `TopologyAnalyzer.py` file in your main project folder.
2.  **Organize files**: Ensure your tree files are located in the directory specified by `TREE_DIR`.
3.  **Edit the script**: Open `TopologyAnalyzer.py` in a text editor and modify the variables in the "USER CONFIGURATION AREA" to match your dataset and analysis parameters.
4.  **Execute the script**: Run the script from your terminal.

        python TopologyAnalyzer.py

The script will then print its progress and a final summary to the console.

## Output Explanation

The script generates three types of output:

### Console Output
A summary is printed directly to your terminal after the analysis is complete. It shows the total number of files processed and, for each SOI-A-B combination, the final counts for each relationship category.

### CSV Output File
-   A CSV file (named according to `OUTPUT_CSV_FILE`) is created with a detailed summary.
-   Each row corresponds to one `(SOI, Group A species, Group B species)` analysis.
-   Columns include the names of the species, the total number of trees where all three were present, and the final counts for "Closer to A", "Closer to B", and "Undetermined/Low Support".

### Fixed Trees Directory
-   A new folder (named according to `MODIFIED_TREE_DIR`) is created.
-   This folder contains copies of all your input trees that have been automatically repaired by the script. These repaired trees are safe to use in other phylogenetic software that requires strict Newick formatting (like `ete3`).
