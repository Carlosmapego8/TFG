import os
import subprocess
from pathlib import Path


class DbtTransformation:
    """
    Ejecuta un comando dbt (por defecto 'build') sobre un proyecto dbt.
    Si no se indica `dbt_executable`, intenta usar el dbt.exe del venv
    en `<project_dir>/venv_dbt_core/Scripts/dbt.exe`; si no existe,
    cae al `dbt` del PATH.
    """

    def __init__(
        self,
        project_dir: str,
        dbt_executable: str = None,
        command: str = "build",
        target: str = None,
        select: str = None,
    ):
        self.project_dir = os.path.abspath(project_dir)
        self.command = command
        self.target = target
        self.select = select

        if dbt_executable is None:
            venv_dbt = Path(self.project_dir) / "venv_dbt_core" / "Scripts" / "dbt.exe"
            self.dbt_executable = str(venv_dbt) if venv_dbt.exists() else "dbt"
        else:
            self.dbt_executable = dbt_executable

    def run(self):
        if not os.path.isdir(self.project_dir):
            raise FileNotFoundError(f"No existe el dbt project_dir: {self.project_dir}")

        args = [self.dbt_executable, self.command, "--project-dir", self.project_dir]
        if self.target:
            args += ["--target", self.target]
        if self.select:
            args += ["--select", self.select]

        print(f"\n[INFO] dbt {self.command} -> {self.project_dir}")
        print(f"[INFO] cmd: {' '.join(args)}")

        result = subprocess.run(args)
        if result.returncode != 0:
            raise RuntimeError(
                f"dbt {self.command} falló con código de salida {result.returncode}"
            )
        print(f"[OK] dbt {self.command} completado")
