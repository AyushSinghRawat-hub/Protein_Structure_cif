import streamlit as st
import os
import json
import subprocess
import glob
from pathlib import Path
import tempfile
import shutil
import time
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Protenix Protein Structure Prediction",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
OUTPUT_DIR = "./output"
EXAMPLES_DIR = "./examples"

# Simple authentication credentials (In production, use proper authentication)
VALID_CREDENTIALS = {
    "admin@example.com": "password123",
    "user@example.com": "userpass",
    # Add more users as needed
}

def authenticate_user(email: str, password: str) -> bool:
    """Simple authentication check"""
    return VALID_CREDENTIALS.get(email) == password

def save_json_file(uploaded_file) -> str:
    """Save uploaded JSON file to examples directory"""
    try:
        # Ensure examples directory exists
        os.makedirs(EXAMPLES_DIR, exist_ok=True)
        
        # Create a short filename to avoid path length issues
        timestamp = datetime.now().strftime("%H%M%S")
        # Get file extension
        file_ext = os.path.splitext(uploaded_file.name)[1]
        # Create short filename
        filename = f"input_{timestamp}{file_ext}"
        file_path = os.path.join(EXAMPLES_DIR, filename)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        st.error(f"Failed to save JSON file: {str(e)}")
        return None

def run_protenix_prediction(json_path: str) -> tuple:
    """Run Protenix prediction command and return success status and output"""
    try:
        # Ensure output directory exists and is clean
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Construct the command
        cmd = [
            "protenix", "predict",
            "--input", json_path,
            "--out_dir", OUTPUT_DIR,
            "--seeds", "101",
            "--model_name", "protenix_base_default_v0.5.0"
        ]
        
        # Display command being executed
        st.info(f"Executing command: {' '.join(cmd)}")
        
        # Create a placeholder for real-time output
        output_placeholder = st.empty()
        
        with st.spinner("Running Protenix prediction... This may take several minutes."):
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Capture output in real-time
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
                    # Update the display with latest output (last 10 lines)
                    recent_output = '\n'.join(output_lines[-10:])
                    output_placeholder.code(recent_output, language='bash')
            
            # Get the return code
            return_code = process.poll()
            
            if return_code == 0:
                st.success("✅ Protenix prediction completed successfully!")
                return True, '\n'.join(output_lines)
            else:
                st.error(f"❌ Protenix prediction failed with return code: {return_code}")
                return False, '\n'.join(output_lines)
                
    except FileNotFoundError:
        error_msg = "❌ 'protenix' command not found. Please ensure Protenix is installed and in your PATH."
        st.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ Error running prediction: {str(e)}"
        st.error(error_msg)
        return False, error_msg

def get_output_files() -> dict:
    """Get all files from output directory organized by type"""
    files_dict = {
        'cif': [],
        'pdb': [],
        'json': [],
        'log': [],
        'other': []
    }
    
    try:
        if not os.path.exists(OUTPUT_DIR):
            return files_dict
            
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = file.lower().split('.')[-1]
                
                if file_ext in files_dict:
                    files_dict[file_ext].append(file_path)
                else:
                    files_dict['other'].append(file_path)
                    
    except Exception as e:
        st.error(f"Error reading output directory: {str(e)}")
    
    return files_dict

def display_protein_structure(cif_file_path: str):
    """Display protein structure using Streamlit Molstar or fallback"""
    try:
        with open(cif_file_path, 'r') as f:
            cif_content = f.read()
        
        # Try to use streamlit-molstar if available
        try:
            from streamlit_molstar import st_molstar
            
            # Create a short, unique key to avoid "File name too long" error
            file_hash = str(hash(cif_file_path))[-8:]  # Last 8 chars of hash
            short_key = f"mol_{file_hash}"
            
            st_molstar(
                cif_content,
                height=600,
                key=short_key
            )
            
        except ImportError:
            st.warning("📦 streamlit-molstar not installed. Install with: `pip install streamlit-molstar`")
            
            # Fallback: display file info and content preview
            st.info(f"📁 CIF file: {os.path.basename(cif_file_path)}")
            st.text(f"Size: {len(cif_content)} characters")
            
            with st.expander("🔍 View CIF content (first 1000 characters)"):
                st.code(cif_content[:1000] + ("..." if len(cif_content) > 1000 else ""), language='text')
                
    except Exception as e:
        st.error(f"Error displaying structure: {str(e)}")

def display_file_content(file_path: str, file_type: str):
    """Display file content based on type"""
    try:
        file_size = os.path.getsize(file_path)
        st.text(f"📏 Size: {file_size:,} bytes")
        
        if file_type == 'json':
            with open(file_path, 'r') as f:
                json_data = json.load(f)
            st.json(json_data)
            
        elif file_type in ['log', 'txt']:
            with open(file_path, 'r') as f:
                content = f.read()
            st.code(content, language='text')
            
        elif file_type == 'cif':
            display_protein_structure(file_path)
            
        elif file_type == 'pdb':
            with open(file_path, 'r') as f:
                content = f.read()
            st.code(content[:1000] + ("..." if len(content) > 1000 else ""), language='text')
            
    except Exception as e:
        st.error(f"Error displaying file content: {str(e)}")

def main():
    st.title("🧬 Protenix Protein Structure Prediction")
    st.markdown("*EC2 Server Implementation*")
    st.markdown("---")
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    
    # Authentication section
    if not st.session_state.authenticated:
        st.header("🔐 User Authentication")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="user@example.com")
            password = st.text_input("Password", type="password")
            
            login_button = st.form_submit_button("🚀 Login", type="primary")
            
            if login_button:
                if authenticate_user(email, password):
                    st.session_state.authenticated = True
                    st.session_state.username = email.split('@')[0]
                    st.success("✅ Authentication successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")
        return
    
    # Main application header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"✅ Logged in as: {st.session_state.username}")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()
    
    st.markdown("---")
    
    # File upload section
    st.header("📁 Upload JSON Input File")
    
    uploaded_file = st.file_uploader(
        "Choose a JSON file for Protenix prediction",
        type="json",
        help="Upload the JSON file containing protein structure prediction parameters"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.success(f"📄 File uploaded: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")
        
        # Preview JSON content
        try:
            json_content = json.loads(uploaded_file.getvalue())
            with st.expander("🔍 Preview JSON content"):
                st.json(json_content)
                
            # Run prediction button
            if st.button("🚀 Run Protenix Prediction", type="primary", use_container_width=True):
                    # Save JSON file
                    json_path = save_json_file(uploaded_file)
                    
                    if json_path:
                        st.info(f"💾 JSON file saved to: `{json_path}`")
                        
                        # Run prediction
                        success, output = run_protenix_prediction(json_path)
                        
                        # Display command output
                        with st.expander("📋 Command Output Log"):
                            st.code(output, language='bash')
                        
                        if success:
                            # Display results
                            st.header("🎯 Prediction Results")
                            
                            # Get output files
                            output_files = get_output_files()
                            
                            # Summary
                            total_files = sum(len(files) for files in output_files.values())
                            st.info(f"📊 Generated {total_files} output files")
                            
                            # Display files by type
                            for file_type, files in output_files.items():
                                if files:
                                    st.subheader(f"📁 {file_type.upper()} Files ({len(files)})")
                                    
                                    for file_path in files:
                                        filename = os.path.basename(file_path)
                                        # Create shorter display name if filename is too long
                                        display_name = filename if len(filename) <= 50 else f"{filename[:20]}...{filename[-20:]}"
                                        
                                        with st.expander(f"📄 {display_name}"):
                                            col1, col2 = st.columns([3, 1])
                                            
                                            with col1:
                                                display_file_content(file_path, file_type)
                                            
                                            with col2:
                                                # Download button with short key
                                                file_hash = str(hash(file_path))[-6:]
                                                download_key = f"dl_{file_hash}"
                                                
                                                try:
                                                    with open(file_path, 'rb') as f:
                                                        st.download_button(
                                                            label="💾 Download",
                                                            data=f.read(),
                                                            file_name=filename,
                                                            mime="application/octet-stream",
                                                            key=download_key
                                                        )
                                                except Exception as e:
                                                    st.error(f"Download error: {e}")
                        else:
                            st.error("❌ Prediction failed. Check the command output above for details.")
                            
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON file: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    # Sidebar with system info
    with st.sidebar:
        st.header("ℹ️ System Information")
        
        # Server info
        st.markdown("**🖥️ Server Status:**")
        try:
            # Check if protenix is available
            result = subprocess.run(['which', 'protenix'], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Protenix available")
                protenix_path = result.stdout.strip()
                st.code(f"Path: {protenix_path}")
            else:
                st.error("❌ Protenix not found")
        except:
            st.warning("⚠️ Cannot check Protenix status")
        
        # Directory info
        st.markdown("**📁 Directories:**")
        st.code(f"Examples: {EXAMPLES_DIR}")
        st.code(f"Output: {OUTPUT_DIR}")
        
        # Current working directory
        st.code(f"PWD: {os.getcwd()}")
        
        # Recent files
        if os.path.exists(OUTPUT_DIR):
            recent_files = []
            for root, dirs, files in os.walk(OUTPUT_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    recent_files.append((file_path, os.path.getmtime(file_path)))
            
            if recent_files:
                st.markdown("**📋 Recent Output Files:**")
                recent_files.sort(key=lambda x: x[1], reverse=True)
                for file_path, _ in recent_files[:5]:
                    st.text(f"• {os.path.basename(file_path)}")

if __name__ == "__main__":
    main()