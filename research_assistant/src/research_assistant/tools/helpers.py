import yaml

class IndentDumper(yaml.SafeDumper):
    """
    Custom YAML Dumper to adjust indentation for better readability.
    """
    def increase_indent(self, flow=False, indentless=False):
        # Ensure that list items are indented properly
        return super(IndentDumper, self).increase_indent(flow, False)

def write_sequences_to_yaml(sequences, output_file):
    """
    Write a list of sequences to a YAML file in the specified format with proper indentation.

    Parameters:
        sequences (list): List of protein sequences as strings.
        output_file (str): Path to the YAML file to write.

    # Example usage:
    ```python
    sequences = [
        "QLEDSEVEAVAKGLEEMYANGVTEDNFKNYVKNNFAQQEISSVEEELNVNISDSCVANKIKDEFFAMISISAIVKAAQKKAWKELAVTVLRFAKANGLKTNAIIVAGQLALWAVQCG",
        "MRYAFAAEATTCNAFWRNVDMTVTALYEVPLGVCTQDPDRWTTTPDDEAKTLCRACPRRWLCARDAVESAGAEGLWAGVVIPESGRARAFALGQLRSLAERNGYPVRDHRVSAQSA"
        ]
    write_sequences_to_yaml(sequences, "output.yaml")
    ```
    """
    if not sequences:
        raise ValueError("The sequences list cannot be empty.")
    
    # YAML structure
    yaml_data = {
        "version": 1,  # Optional, defaults to 1
        "sequences": []
    }

    # Generate sequence entries with unique IDs
    for i, seq in enumerate(sequences):
        entry = {
            "protein": {
                "id": chr(65 + i),  # 'A', 'B', 'C', ...
                "sequence": seq
            }
        }
        yaml_data["sequences"].append(entry)

    # Write to the output file with proper formatting and indentation
    with open(output_file, 'w') as file:
        yaml.dump(
            yaml_data, 
            file, 
            Dumper=IndentDumper,        # Use the custom dumper
            default_flow_style=False, 
            sort_keys=False,            # Ensures 'version' stays at the top
            indent=2,                   # Increased indentation for better readability
        )


def get_run_id():
    """
    Get a run ID in the format of YYMMDD-HHMM, e.g. 241201-1430
    """
    from datetime import datetime
    return datetime.now().strftime("run-date-%y%m%d-time-%H%M")