#!/usr/bin/env python3
"""Empacota cada entrega em deliverables/<entrega>.zip."""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PKGS = ROOT / "packages"
APPS = ROOT / "apps"
DELIV = ROOT / "deliverables"
DELIV.mkdir(parents=True, exist_ok=True)


def make_zip(zip_name: str, entries: list[tuple[Path, str]]):
    out = DELIV / zip_name
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in entries:
            if src.is_dir():
                for f in sorted(src.rglob("*")):
                    if f.is_file() and "__pycache__" not in f.parts and ".pytest_cache" not in f.parts:
                        zf.write(f, str(Path(arcname) / f.relative_to(src)))
            elif src.exists():
                zf.write(src, arcname)
            else:
                raise FileNotFoundError(f"Arquivo ausente para pacote {zip_name}: {src}")
    print(f"[ZIP] {out} ({out.stat().st_size // 1024} KB)")


def main():
    make_zip("01-ai-challenges-dossie.zip", [
        (DOCS / "01-ai-challenges" / "01_RespiraCidadao_Dossie_Integrador.pdf", "01_RespiraCidadao_Dossie_Integrador.pdf"),
        (DOCS / "01-ai-challenges" / "01_RespiraCidadao_Dossie_Integrador.docx", "01_RespiraCidadao_Dossie_Integrador.docx"),
        (DOCS / "assets", "imagens"),
        (DOCS / "ENTREGAS.md", "ENTREGAS_E_ROTEIROS.md"),
    ])

    make_zip("02-aicss-iot.zip", [
        (DOCS / "02-ai-computer-systems-and-sensors" / "02_RespiraCidadao_AICSS_IoT.pdf", "02_RespiraCidadao_AICSS_IoT.pdf"),
        (DOCS / "02-ai-computer-systems-and-sensors" / "02_RespiraCidadao_AICSS_IoT.docx", "02_RespiraCidadao_AICSS_IoT.docx"),
        (PKGS / "iot-aicss" / "sketch.ino", "codigo/sketch.ino"),
        (PKGS / "iot-aicss" / "diagram.json", "codigo/diagram.json"),
        (PKGS / "iot-aicss" / "libraries.txt", "codigo/libraries.txt"),
        (PKGS / "iot-aicss" / "receiver_csv.py", "codigo/receiver_csv.py"),
        (PKGS / "iot-aicss" / "run_3_cenarios.py", "codigo/run_3_cenarios.py"),
        (PKGS / "iot-aicss" / "README.md", "README.md"),
        (PKGS / "iot-aicss" / "evidencias", "evidencias"),
    ])

    make_zip("03-cognitive-cybersecurity.zip", [
        (DOCS / "03-cognitive-cybersecurity" / "03_RespiraCidadao_Cybersecurity.pdf", "03_RespiraCidadao_Cybersecurity.pdf"),
        (DOCS / "03-cognitive-cybersecurity" / "03_RespiraCidadao_Cybersecurity.docx", "03_RespiraCidadao_Cybersecurity.docx"),
        (APPS / "api" / "app" / "security.py", "evidencias/security.py"),
        (APPS / "api" / "tests" / "test_api.py", "evidencias/test_api.py"),
        (DOCS / "evidencias" / "03_limite_chave.png", "evidencias/03_limite_chave.png"),
        (DOCS / "evidencias" / "03_selo.png", "evidencias/03_selo.png"),
        (DOCS / "evidencias" / "03_pytest.png", "evidencias/03_pytest.png"),
        (DOCS / "evidencias" / "07_aws_rds_console.png", "evidencias/07_aws_rds_console.png"),
    ])

    make_zip("04-cognitive-data-science-oracle.zip", [
        (PKGS / "data-science-oracle" / "queries_inclusive_mobility_rover.sql", "queries_inclusive_mobility_rover.sql"),
        (PKGS / "data-science-oracle" / "README.md", "README.md"),
    ])

    make_zip("05-computational-thinking-python.zip", [
        (DOCS / "05-computational-thinking-with-python" / "05_RespiraCidadao_API_Python.pdf", "05_RespiraCidadao_API_Python.pdf"),
        (DOCS / "05-computational-thinking-with-python" / "05_RespiraCidadao_API_Python.docx", "05_RespiraCidadao_API_Python.docx"),
        (APPS / "api" / "app", "api/app"),
        (APPS / "api" / "tests" / "test_api.py", "api/tests/test_api.py"),
        (APPS / "api" / "pyproject.toml", "api/pyproject.toml"),
    ])

    make_zip("06-machine-learning-modelling.zip", [
        (PKGS / "ml-modelling" / "respira_ml_modelling.ipynb", "respira_ml_modelling.ipynb"),
        (DOCS / "06_RespiraCidadao_ML_Slides.pptx", "06_RespiraCidadao_ML_Slides.pptx"),
        (DOCS / "06-machine-learning-and-modelling" / "06_RespiraCidadao_ML_Resumo.pdf", "06_RespiraCidadao_ML_Resumo.pdf"),
        (DOCS / "06-machine-learning-and-modelling" / "06_RespiraCidadao_ML_Resumo.docx", "06_RespiraCidadao_ML_Resumo.docx"),
        (PKGS / "ml-modelling" / "charts", "charts"),
    ])

    make_zip("07-cloud-serverless.zip", [
        (DOCS / "07-plataformas-servicos-cognitivos-cloud" / "07_RespiraCidadao_Cloud_Serverless.pdf", "07_RespiraCidadao_Cloud_Serverless.pdf"),
        (DOCS / "07-plataformas-servicos-cognitivos-cloud" / "07_RespiraCidadao_Cloud_Serverless.docx", "07_RespiraCidadao_Cloud_Serverless.docx"),
        (PKGS / "cloud-serverless" / "lambda_function.py", "lambda_function.py"),
        (PKGS / "cloud-serverless" / "tabela_ocorrencias.sql", "tabela_ocorrencias.sql"),
        (PKGS / "cloud-serverless" / "simulador_dispositivo.py", "simulador_dispositivo.py"),
        (PKGS / "cloud-serverless" / "servidor_local.py", "servidor_local.py"),
        (PKGS / "cloud-serverless" / "teste_local.py", "teste_local.py"),
        (PKGS / "cloud-serverless" / "deploy_aws.sh", "deploy_aws.sh"),
        (PKGS / "cloud-serverless" / "run_sql.py", "run_sql.py"),
        (PKGS / "cloud-serverless" / "requirements.txt", "requirements.txt"),
        (PKGS / "cloud-serverless" / "README.md", "README.md"),
        (DOCS / "evidencias" / "07_aws_lambda_env.png", "evidencias/01_lambda_env.png"),
        (DOCS / "evidencias" / "07_aws_simulador.png", "evidencias/02_simulador_aws.png"),
        (DOCS / "evidencias" / "07_aws_cloudwatch.png", "evidencias/03_cloudwatch_logs.png"),
        (DOCS / "evidencias" / "07_aws_rds_console.png", "evidencias/04_rds_console.png"),
        (DOCS / "evidencias" / "07_aws_rds_select.png", "evidencias/05_rds_select.png"),
    ])

    make_zip("08-redes-neurais-deep-learning.zip", [
        (PKGS / "neural-networks" / "respira_neural_network.ipynb", "respira_neural_network.ipynb"),
        (DOCS / "08-redes-neurais-deep-learning-ag" / "08_RespiraCidadao_Redes_Neurais.pdf", "08_RespiraCidadao_Redes_Neurais.pdf"),
        (DOCS / "08-redes-neurais-deep-learning-ag" / "08_RespiraCidadao_Redes_Neurais.docx", "08_RespiraCidadao_Redes_Neurais.docx"),
        (PKGS / "neural-networks" / "charts", "charts"),
    ])

    make_zip("09-statistical-computing-upload-direto.zip", [
        (PKGS / "stats-r-python" / "air_quality_clean.csv", "air_quality_clean.csv"),
        (PKGS / "stats-r-python" / "analise_estatistica.py", "analise_estatistica.py"),
        (DOCS / "09-statistical-computing-r-python" / "09_RespiraCidadao_Relatorio_Estatistico.pdf", "09_RespiraCidadao_Relatorio_Estatistico.pdf"),
    ])


if __name__ == "__main__":
    main()
