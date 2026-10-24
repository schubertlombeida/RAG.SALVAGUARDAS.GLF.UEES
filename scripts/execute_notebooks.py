"""Ejecuta cinco cuadernos con el mismo intérprete y un kernel temporal local."""
import json
import os
from pathlib import Path
import sys
import tempfile
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="glf-kernel-") as folder:
    path = Path(folder) / "kernels/glf-academic"
    path.mkdir(parents=True)
    (path / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                                               "display_name": "GLF académico", "language": "python"}), encoding="utf-8")
    os.environ["JUPYTER_PATH"] = folder
    os.environ["IPYTHONDIR"] = str(Path(folder)/"ipython")
    for file in sorted((root / "notebooks").glob("*.ipynb")):
        book = nbformat.read(file, as_version=4)
        NotebookClient(book, timeout=180, kernel_name="glf-academic", resources={"metadata": {"path": str(root)}}).execute()
        nbformat.write(book, file)
        print(file.name + ": ejecutado sin errores")
