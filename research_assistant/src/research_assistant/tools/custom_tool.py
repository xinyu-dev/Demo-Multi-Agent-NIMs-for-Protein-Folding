from crewai.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field
import os, shutil, requests
from loguru import logger
from abnumber import Chain
from igfold import IgFoldRunner



def is_amino_acid_sequence(seq):

    # Clean the sequence (remove spaces and newlines, convert to uppercase)
    seq = "".join(seq.split()).upper()
    # Define valid amino acid characters
    valid_amino_acids = set("ARNDCEQGHILKMFPSTWYVBZX*")
    
    # Check if all characters in the sequence are valid amino acids
    return all(char in valid_amino_acids for char in seq)

def process_mab_sequence(seq):
    result = {
        'seq': None,
        'description': "Not a valid antibody sequence",
        'is_vh': False,
        'is_vl': False
    }
    try:
        # this line can generate an error if the sequence is not a valid antibody sequence
        chain = Chain(seq, scheme='kabat')

        # antibody content is detected. process the sequence based on the type of chain
        if chain.is_heavy_chain():
            result['seq'] = chain.seq
            result['description'] = 'Heavy chain detected. Processed into a VH chain'
            result['is_vh'] = True
        elif chain.is_light_chain():
            result['seq'] = chain.seq
            result['description'] = 'Light chain detected. Processed into a VL chain'
            result['is_vl'] = True
        else:
            # return the default result
            pass
    except:
        # return the default result
        pass

    return result


def preprare_directory(temp, delete_old=True):
    """
    Create a new directory and delete the old one if it exists
    :param temp: str: path to the directory
    :param delete_old: bool, whether to delete the old directory. Defaults to True.
    """
    if delete_old:  
        if os.path.exists(temp):
            # Remove the directory and all its contents
            shutil.rmtree(temp)
    # Recreate the directory
    os.makedirs(temp, exist_ok=True)



class PreprocessInput(BaseModel):
    """Input schema for Preprocess."""
    protein_name: str = Field(default="protein_1", description="Name or ID of the sequence. Try to infer from user input. If not possible, you can use 'protein_1', 'protein_2', etc.")
    num_chains: int = Field(default = 0, description="Number of chains in the protein")
    sequences: List[str] = Field(description="List of input sequences from the user", default = [])

class SequenceMetadata(BaseModel):
    clean_sequence: str = Field(description="Cleaned sequence", default = "")
    description: str = Field(description="Description of the sequence", default = "")
    is_mab: bool = Field(description="Whether the sequence is an antibody", default = False)
    vh_or_vl: str = Field(description="VH or VL chain", default = "")
    is_valid_sequence: bool = Field(description="Whether the sequence is a valid amino acid sequence", default = False)

class PreprocessOutput(BaseModel):
    """Output schema for Preprocess."""
    protein_name: str = Field(description="Name of the sequence", default = "protein_1")
    num_chains: int = Field(description="Number of chains in the protein", default = 0)
    sequence_metadata: Dict[str, SequenceMetadata] = Field(description="Metadata of each sequence in the protein", default=0)


class Preprocess(BaseTool):
    name: str = "Preprocess"
    description: str = (
        """
        The tool returns the cleaned sequence along with other information
        """
    )
    args_schema: Type[BaseModel] = PreprocessInput

    def _process_monomer(self, sequence: str) -> SequenceMetadata:

        metadata = SequenceMetadata()

        # check if the sequence is a valid amino acid sequence
        if is_amino_acid_sequence(sequence):
            # try to read a 
            metadata.clean_sequence = sequence
            metadata.is_valid_sequence = True

            # check mab content
            mab_result = process_mab_sequence(sequence)
            # if the sequence is an antibody, update the result
            if mab_result['seq'] is not None:
                metadata.clean_sequence = mab_result['seq']
                metadata.description = mab_result['description']
                metadata.is_mab = True
                metadata.vh_or_vl = 'VH' if mab_result['is_vh'] else 'VL' # Abnumber can only do VH or VL, not both
            else:
                metadata.description = "The sequence appears to be a valid protein sequence, but not a valid antibody sequence"
        
        return metadata

    def _run(self, protein_name: str, num_chains: int, sequences: List[str]) -> str:

        sequence_metadata = {}

        # process monomer
        if len(sequences) == 1:
            seq1_metadata = self._process_monomer(sequences[0])
            sequence_metadata['seq1'] = seq1_metadata

        # process dimer
        elif len(sequences) == 2:
            seq1_metadata = self._process_monomer(sequences[0])
            seq2_metadata = self._process_monomer(sequences[1])
            sequence_metadata['seq1'] = seq1_metadata
            sequence_metadata['seq2'] = seq2_metadata
        else:
            pass

        # return the result
        result = PreprocessOutput(
            protein_name=protein_name,
            num_chains=num_chains,
            sequence_metadata=sequence_metadata
        )

        # must return string representation of the pydantic object, 
        # otherwise when you pass to the next agent, you will get an error!
        return str(result)


class ModelSelectionOutput(BaseModel):
    """Output schema for ModelSelection."""
    selected_models: list[str] = Field(description="List of selected models", default = [])

    explanation: str = Field(description="Explanation of why you selected some models, and why other models aren't selected", default = "")


class ESMFoldPlayground:
    def __init__(self, NGC_API_KEY, query_url=None):
        """
        Initialize the ESMFoldPlayground class
        NGC_API_KEY: str, the API key to use
        query_url: str, the url to send the request to, default is the ESMFold NIM endpoint
        """
        self.NGC_API_KEY = NGC_API_KEY
        self.query_url = query_url if query_url is not None else "https://health.api.nvidia.com/v1/biology/nvidia/esmfold"

    
    def predict(self,sequence, output_dir=None, output_file_name="predicted_protein.pdb", delete_old_dir=False):
        """
        Main function to run the molecular docking
        sequence: str, single aa sequence
        output_dir: str, the directory to save the output to. If there are existing contents, it will be deleted and recreated. Defaults to None, and it will not save the output PDB file. 
        output_file_name: str, the name of the output PDB file. Defaults to "predicted_protein.pdb". Only used when output_dir is not None.
        delete_old_dir: bool, whether to delete the old directory. Defaults to True.
        return response object
        """

        # prepare output directory
        if output_dir is not None:
            logger.info(f"Preparing output directory: {output_dir}")
            preprare_directory(output_dir, delete_old=delete_old_dir)
        
        # prepare data
        data = {
            "sequence": sequence,
        }

        # prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.NGC_API_KEY}"
        }
        
        # send request
        logger.info(f"Sending request to {self.query_url}")
        response = requests.post(self.query_url, headers=headers, json=data)
        
        # check response
        if response.status_code == 200:
            logger.success("Request successful")
            # get the result
            result = response.json()
            # Write PDB file
            if output_dir is not None:
                fp = os.path.join(output_dir, output_file_name)
                with open(fp, "w") as f:
                    f.write(result["pdbs"][0])
        else:
            logger.error(f"Request failed with status code {response.status_code}. Output file will not be saved.")
            logger.error("Response content:", response.content)
            
        return response
    

def predict_with_esmfold(sequence, output_dir="output/esmfold_result", output_file_name="predicted_protein.pdb", delete_old_dir=True):
    # get NGC API key
    NGC_API_KEY = os.getenv("NVIDIA_NIM_API_KEY")

    # initialize the ESMFoldPlayground class
    esmfold_playground = ESMFoldPlayground(
        NGC_API_KEY=NGC_API_KEY
    )

    # run prediction
    output_file_path = os.path.join(output_dir, output_file_name)
    try: 
        response = esmfold_playground.predict(
            sequence=sequence,
            output_dir=output_dir,
            output_file_name=output_file_name,
            delete_old_dir=delete_old_dir
        )
        if response.status_code == 200:
            return {
                'success': True,
                'output_file_path': output_file_path, 
                'error': None
            }
        else:
            return {
                'success': False,
                'error': response.content, 
                'output_file_path': None
            }

    except Exception as e:
        print(f"Failed to predict with ESMFold with error: {e}")
        return {
            'success': False,
            'error': str(e), 
            'output_file_path': None
        }
    

class FoldToolOutput(BaseModel):
    """Output schema for different protein folding tools."""
    model_name: str = Field(description="Name of the protein folding tool", default = "")
    model_is_selected: bool = Field(description="Whether the model is selected by the model_selection_agent", default = False)
    success: bool = Field(description="Whether the prediction is successful", default = False)
    output_file_path: str = Field(description="Path to the output PDB file of the predicted structure", default = "")


class ESMFoldToolInput(BaseModel):
    """Input schema for ESMFoldTool."""
    selected_models: List[str] = Field(description="List of selected models", default = [])
    protein_name: str = Field(description="Name of the protein", default = "")
    sequence: str = Field(description="Clean amino acid sequence of the protein that will be used for prediction", default = None)


class ESMFoldTool(BaseTool):

    name: str = "Using ESMFold to predict protein structure"
    description: str = "Use ESMFold to predict the structure of a protein"
    args_schema: Type[BaseModel] = ESMFoldToolInput

    def _run(self, selected_models: List[str], protein_name: str, sequence: str) -> str:

        # directory to save the output
        output_base_dir = "output/esmfold_result"

        result = FoldToolOutput(
            model_name="ESMFold",
        )

        # check if ESMFold is in the selected models
        if "ESMFold" not in selected_models:
            result.model_is_selected = False
            result.output_file_path = None
            result.success = False
        else:
            # generate output file name
            output_file_name= f"{protein_name}.pdb"
            
            # predict the structure
            logger.info(f"Predicting the structure of {protein_name} with ESMFold")
            pred_r = predict_with_esmfold(sequence, output_dir=output_base_dir, output_file_name=output_file_name)

            # update the result
            result.success = pred_r['success']
            result.output_file_path = pred_r['output_file_path']
            result.model_is_selected = True
        
        return str(result)
    

def predict_with_igfold(vh_sequence, vl_sequence, output_dir="output/igfold_result", output_file_name="predicted_antibody.pdb", delete_old_dir=True):

    """
    Predict the structure of an antibody with IgFold
    vh_sequence: str, clean amino acid sequence of the VH chain
    vl_sequence: str, clean amino acid sequence of the VL chain
    output_dir: str, the directory to save the output to. If there are existing contents, it will be deleted and recreated. Defaults to None, and it will not save the output PDB file. 
    output_file_name: str, the name of the output PDB file. Defaults to "predicted_antibody.pdb". Only used when output_dir is not None.
    delete_old_dir: bool, whether to delete the old directory. Defaults to True.
    return: dict, the result of the prediction
    """

    # example input seuquence for IgFold
    #     sequences = {
    # "H": "EVQLVQSGPEVKKPGTSVKVSCKASGFTFMSSAVQWVRQARGQRLEWIGWIVIGSGNTNYAQKFQERVTITRDMSTSTAYMELSSLRSEDTAVYYCAAPYCSSISCNDGFDIWGQGTMVTVS",
    #"L": "DVVMTQTPFSLPVSLGDQASISCRSSQSLVHSNGNTYLHWYLQKPGQSPKLLIYKVSNRFSGVPDRFSGSGSGTDFTLKISRVEAEDLGVYFCSQSTHVPYTFGGGTKLEIK"
    #}

    logger.info(f"Predicting the structure of antibody with IgFold")
    sequences = {}
    if vh_sequence is not None and len(vh_sequence) > 1: 
        sequences['H'] = vh_sequence
    if vl_sequence is not None and len(vl_sequence) > 1:
        sequences['L'] = vl_sequence

    logger.info(f"Input sequences for IgFold model: {sequences}")

    preprare_directory(output_dir, delete_old=False)
    fp = os.path.join(output_dir, output_file_name)

    try:
        # IgFold will raise error if there is any issue with teh input seqeunce 
        igfold = IgFoldRunner()
        igfold.fold(
            fp, # Output PDB file
            sequences=sequences, # Antibody sequences
            do_refine=False, # Refine the antibody structure with PyRosetta
            do_renum=False, # Renumber predicted antibody structure (Chothia)
        )
        logger.success(f"IgFold successfully predicted the structure of antibody and saved to {fp}")
        return {
            'success': True,
            'output_file_path': fp, 
            'error': None
        }
    except Exception as e:
        logger.error(f"Failed to predict the structure of antibody with IgFold with error: {e}")
        return {
            'success': False,
            'error': str(e), 
            'output_file_path': None
        }
        
class IgFoldToolInput(BaseModel):
    """
    Input schema for IgFoldTool
    """
    selected_models: List[str] = Field(description="List of selected models", default = [])
    protein_name: str = Field(description="Name of the protein", default = "")
    vh_sequence: str = Field(description="Clean amino acid sequence of the VH chain that will be used for prediction", default = None)
    vl_sequence: str = Field(description="Clean amino acid sequence of the VL chain that will be used for prediction", default = None)

class IgFoldTool(BaseTool):
    name: str = "Using IgFold to predict antibody structure"
    description: str = "Use IgFold to predict the structure of an antibody"
    args_schema: Type[BaseModel] = IgFoldToolInput

    def _run(self, selected_models: List[str], protein_name: str, vh_sequence: str, vl_sequence: str) -> str:

        output_base_dir = "output/igfold_result"

        result = FoldToolOutput(
            model_name="IgFold",
        )

        # check if IgFold is in the selected models
        if "IgFold" not in selected_models:
            result.model_is_selected = False
            result.output_file_path = None
            result.success = False
        else:
            # generate output file name
            output_file_name= f"{protein_name}.pdb"
            
            # predict the structure
            logger.info(f"Predicting the structure of {protein_name} with IgFold")
            pred_r = predict_with_igfold(vh_sequence, vl_sequence, output_dir=output_base_dir, output_file_name=output_file_name)

            # update the result
            result.success = pred_r['success']
            result.output_file_path = pred_r['output_file_path']
            result.model_is_selected = True

        return str(result)