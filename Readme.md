Protein Structure Viewer 🧬
A powerful Streamlit-based web application for visualizing and analyzing protein structures from CIF files. This interactive tool provides comprehensive 3D visualization and structural analysis capabilities.
Features
🎭 3D Visualization

Interactive molecular structure viewer using py3Dmol
Multiple representation styles: Cartoon, Ribbon, Stick, Sphere, Line
Customizable color schemes: Spectrum, Chain, Element, Residue
Molecular surface display options
Sidechain and hetero atom visibility controls

📊 Structural Analysis

Unit cell parameter extraction
Residue composition analysis
Chain, residue, and atom counting
Resolution and refinement statistics
Experimental data visualization

💾 Data Management

CIF file upload and parsing
Download original CIF files
Export to PDB format
Structure metadata display

⚙️ Customization

Adjustable background colors
Opacity controls
Multiple viewing angles
Real-time rendering updates

Installation
Prerequisites

Python 3.8+
pip package manager

Step-by-Step Setup

Clone or download the project files
Create a virtual environment (recommended)python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install required packagespip install -r requirements.txt

Or install individually:pip install streamlit biopython py3Dmol matplotlib stmol plotly pandas numpy


Run the applicationstreamlit run protein_viewer.py


Open your browser
The app will automatically open at http://localhost:8501



Usage
Basic Operation

Upload a CIF file using the sidebar file uploader
Customize visualization using the controls in the sidebar:
Select representation style
Choose color scheme
Toggle surface and sidechain visibility
Adjust background and opacity


Explore structure details in the right panel:
View unit cell parameters
See experimental metadata
Analyze residue composition


Use interactive controls in the 3D viewer:
Left-click and drag: Rotate structure
Right-click and drag: Zoom in/out
Middle-click and drag: Pan structure
Right-click menu: Additional options including image export



File Format Support

Primary format: CIF (.cif) files
Export format: PDB (.pdb) conversion available
Coming soon: Direct PDB file upload

Example Workflow

Upload your 7r6r_sample_3.cif file
Select "Cartoon" representation with "Spectrum" coloring
Enable "Surface" view for better depth perception
Click "Analyze Structure" to get residue counts
Use the download buttons to export the structure

Project Structure
protein-structure-viewer/
│
├── protein_viewer.py      # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── assets/               # Optional: images and static files

Requirements
The application requires the following Python packages:

streamlit==1.28.0 - Web application framework
biopython==1.81 - Biological computation library
py3Dmol==0.8.0 - 3D molecular visualization
stmol==0.0.8 - Streamlit integration for py3Dmol
matplotlib==3.7.0 - Plotting and visualization
pandas==2.0.0 - Data manipulation and analysis
numpy==1.24.0 - Numerical computing
plotly==5.15.0 - Interactive charts

Troubleshooting
Common Issues
ModuleNotFoundError
# If you see errors about missing modules:
pip install missing-package-name

Port already in use
streamlit run protein_viewer.py --server.port 8502

CIF parsing errors

Ensure the CIF file is properly formatted
Check for file corruption

3D viewer not loading

Refresh the browser page
Check browser console for errors

Performance Tips

For large structures (>50,000 atoms), consider using simpler representations
Close other browser tabs to improve rendering performance
Use "Line" or "Stick" representations for faster rendering of large structures

Contributing
We welcome contributions! Here's how you can help:

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

Planned Features

Direct PDB file support
Ramachandran plot generation
Distance and angle measurements
Secondary structure analysis
Multiple structure alignment
Session saving/loading

License
This project is open source and available under the MIT License.
Support
If you encounter any issues or have questions:

Check the troubleshooting section above
Search existing issues on GitHub
Create a new issue with:
Detailed description of the problem
Steps to reproduce
Error messages
Your system information



Acknowledgments

Built with Streamlit
3D visualization powered by py3Dmol
Structural biology support from BioPython
Icons from Twemoji
