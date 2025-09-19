import streamlit as st
import py3Dmol
from stmol import showmol
import requests
from io import StringIO
import tempfile
import os
from Bio.PDB import MMCIFParser, PDBList, PDBIO
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
import matplotlib.pyplot as plt
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Protein Structure Viewer",
    page_icon="🧬",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subheader {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">🧬 Protein Structure Viewer</h1>', unsafe_allow_html=True)

# Function to parse CIF file and extract information
def parse_cif_file(cif_content):
    """Parse CIF file and extract basic information"""
    try:
        cif_dict = MMCIF2Dict(StringIO(cif_content))
        
        info = {
            'structure_id': cif_dict.get('_entry.id', ['Unknown'])[0],
            'title': cif_dict.get('_struct.title', ['No title'])[0],
            'deposition_date': cif_dict.get('_pdbx_database_status.recvd_initial_deposition_date', ['Unknown'])[0],
            'resolution': cif_dict.get('_reflns.d_resolution_high', ['Unknown'])[0],
            'space_group': cif_dict.get('_symmetry.space_group_name_H-M', ['Unknown'])[0],
            'cell_params': {
                'a': cif_dict.get('_cell.length_a', ['Unknown'])[0],
                'b': cif_dict.get('_cell.length_b', ['Unknown'])[0],
                'c': cif_dict.get('_cell.length_c', ['Unknown'])[0],
                'alpha': cif_dict.get('_cell.angle_alpha', ['Unknown'])[0],
                'beta': cif_dict.get('_cell.angle_beta', ['Unknown'])[0],
                'gamma': cif_dict.get('_cell.angle_gamma', ['Unknown'])[0]
            }
        }
        return info
    except Exception as e:
        st.error(f"Error parsing CIF file: {e}")
        return None

# Function to create 3D visualization
def render_mol(cif_content, style='cartoon', surface=False, width=800, height=400):
    """Render the molecular structure using py3Dmol"""
    viewer = py3Dmol.view(width=width, height=height)
    viewer.addModel(cif_content, 'cif')
    
    if style == 'cartoon':
        viewer.setStyle({'cartoon': {'color': 'spectrum'}})
    elif style == 'stick':
        viewer.setStyle({'stick': {}})
    elif style == 'sphere':
        viewer.setStyle({'sphere': {'radius': 0.5}})
    elif style == 'line':
        viewer.setStyle({'line': {}})
    
    if surface:
        viewer.addSurface(py3Dmol.VDW, {'opacity': 0.7, 'color': 'white'})
    
    viewer.zoomTo()
    viewer.setBackgroundColor('white')
    return viewer

# Main app functionality
def main():
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Viewer Settings")
        
        # File upload
        uploaded_file = st.file_uploader("Upload CIF file", type=['cif'])
        
        if uploaded_file is not None:
            cif_content = uploaded_file.getvalue().decode("utf-8")
            
            # Parse file information
            file_info = parse_cif_file(cif_content)
            
            if file_info:
                st.markdown("### 📋 File Information")
                st.write(f"**Structure ID:** {file_info['structure_id']}")
                st.write(f"**Title:** {file_info['title']}")
                st.write(f"**Resolution:** {file_info['resolution']} Å")
                st.write(f"**Space Group:** {file_info['space_group']}")
            
            # Visualization options
            st.markdown("### 🎨 Visualization Options")
            style_option = st.selectbox(
                "Representation style",
                ['cartoon', 'stick', 'sphere', 'line'],
                index=0
            )
            
            show_surface = st.checkbox("Show molecular surface", value=False)
            show_sidechains = st.checkbox("Show sidechains", value=False)
            
            # Color options
            color_option = st.selectbox(
                "Color scheme",
                ['spectrum', 'chain', 'element', 'residue'],
                index=0
            )
            
            # Additional options
            st.markdown("### 🔧 Additional Options")
            show_hetero = st.checkbox("Show hetero atoms (water, ligands)", value=True)
            show_hydrogens = st.checkbox("Show hydrogen atoms", value=False)

    # Main content area - Full width for structure visualization
    if uploaded_file is not None:
        st.markdown("### 🎭 3D Structure Visualization")
        
        # Use container for full width
        with st.container():
            # Create visualization in full width - use much larger width for full coverage
            viewer = render_mol(
                cif_content, 
                style=style_option, 
                surface=show_surface,
                width=1800,
                height=600
            )
            
            # Show the molecule in full width with container width
            showmol(viewer, height=600, width=1800)
        
        # Download button for the structure
        st.download_button(
            label="📥 Download CIF File",
            data=cif_content,
            file_name=uploaded_file.name,
            mime="chemical/x-cif"
        )
        
        # Structure details below the visualization
        if file_info:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📊 Structure Details")
                
                # Display cell parameters
                st.markdown("**Unit Cell Parameters:**")
                cell_df = pd.DataFrame.from_dict(file_info['cell_params'], orient='index', columns=['Value'])
                st.dataframe(cell_df, use_container_width=True)
                
                # Additional information
                st.markdown("**Additional Information:**")
                st.write(f"**Deposition Date:** {file_info.get('deposition_date', 'Unknown')}")
            
            with col2:
                # Quick analysis
                st.markdown("### 🔍 Quick Analysis")
                if st.button("Analyze Structure"):
                    with st.spinner("Analyzing structure..."):
                        # Simple analysis - count residues, atoms, etc.
                        try:
                            parser = MMCIFParser(QUIET=True)
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.cif', delete=False) as tmp:
                                tmp.write(cif_content)
                                tmp_path = tmp.name
                            
                            structure = parser.get_structure(file_info['structure_id'], tmp_path)
                            os.unlink(tmp_path)
                            
                            # Count residues and atoms
                            residue_count = 0
                            atom_count = 0
                            chain_count = 0
                            
                            for model in structure:
                                for chain in model:
                                    chain_count += 1
                                    for residue in chain:
                                        residue_count += 1
                                        for atom in residue:
                                            atom_count += 1
                            
                            st.write(f"**Chains:** {chain_count}")
                            st.write(f"**Residues:** {residue_count}")
                            st.write(f"**Atoms:** {atom_count}")
                            
                        except Exception as e:
                            st.error(f"Analysis error: {e}")
        
    else:
        st.info("👈 Please upload a CIF file to get started")
        
        # Example structure
        st.markdown("### 🔍 Example Structure")
        if st.button("Load example structure (7R6R)"):
            # You can replace this with actual CIF content or a URL
            st.info("Example loading functionality would go here")

# Run the app
if __name__ == "__main__":
    main()