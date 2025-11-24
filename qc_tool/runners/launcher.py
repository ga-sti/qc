import os, shutil, subprocess, sys, traceback
from pathlib import Path

DEST_FOLDER = Path(r"C:\QC_Auto")
LOG = DEST_FOLDER / "launcher.log"

def log(msg: str):
    DEST_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def main():
    try:
        project_root = Path(__file__).resolve().parents[2]
        log(f"[i] project_root = {project_root}")

        if DEST_FOLDER.exists():
            shutil.rmtree(DEST_FOLDER, ignore_errors=True)
        ignore = shutil.ignore_patterns('__pycache__','oraculos','build','dist','*.log')
        shutil.copytree(project_root, DEST_FOLDER, ignore=ignore)
        log(f"[i] Copiado a {DEST_FOLDER}")

        python = sys.executable
        # ⚙️ Forzar UTF-8 en el hijo
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        cmd = [python, "-X", "utf8", "-m", "qc_tool.runners.pipeline"]
        log(f"[i] Ejecutando: {cmd} (cwd={DEST_FOLDER})")

        res = subprocess.run(
            cmd,
            cwd=str(DEST_FOLDER),
            capture_output=True,
            text=True,
            encoding="utf-8",   # decodifica stdout/stderr como UTF-8
            env=env
        )
        log(f"[i] returncode = {res.returncode}")
        if res.stdout: log("[stdout]\n" + res.stdout)
        if res.stderr: log("[stderr]\n" + res.stderr)

    except Exception:
        log("[!] Error:\n" + traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
