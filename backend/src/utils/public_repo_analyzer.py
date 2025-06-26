import os
import shutil
import tempfile
import subprocess
from typing import Dict, Any, List

def analyze_public_repository(repo_url: str) -> Dict[str, Any]:
    """Clone a public repository and perform a basic analysis."""
    temp_dir = tempfile.mkdtemp()
    try:
        # Clone the repository
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True, capture_output=True, text=True)

        # Analyze the file structure
        file_structure = _analyze_file_structure(temp_dir)

        # In the future, add more analysis like technology detection, etc.

        return {
            "success": True,
            "repo_url": repo_url,
            "analysis": {
                "file_count": len(file_structure),
                "file_structure": file_structure,
            }
        }
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": f"Failed to clone repository: {e.stderr}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

def _analyze_file_structure(path: str) -> List[Dict[str, Any]]:
    """Walk through the directory and list files and folders."""
    structure = []
    for root, dirs, files in os.walk(path):
        # Exclude .git directory
        if '.git' in dirs:
            dirs.remove('.git')
            
        for name in files:
            relative_path = os.path.relpath(os.path.join(root, name), path)
            structure.append({"path": relative_path, "type": "file"})
        for name in dirs:
            relative_path = os.path.relpath(os.path.join(root, name), path)
            structure.append({"path": relative_path, "type": "dir"})
    return structure
