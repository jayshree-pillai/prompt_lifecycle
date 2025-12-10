from pathlib import Path

PROJECT_ROOT = Path("prompt_lifecycle")

# All directories we want in the project
DIRS = [
    "docs",
    "examples",
    "src/company_overview_engine",
    "src/company_overview_engine/config",
    "src/company_overview_engine/prompts/company_overview",
    "src/company_overview_engine/schemas",
    "src/company_overview_engine/engine",
    "src/company_overview_engine/eval",
    "src/company_overview_engine/eval/datasets",
    "src/company_overview_engine/telemetry",
    "src/company_overview_engine/telemetry/exporters",
    "src/company_overview_engine/cli",
    "src/company_overview_engine/utils",
    "tests",
]

# Files with minimal placeholder content
FILES = {
    # top-level
    "README.md": "# company-overview-engine\n",
    "pyproject.toml": "# TODO: add project metadata and dependencies\n",

    # docs
    "docs/architecture.md": "# Architecture\n",
    "docs/prompt_lifecycle.md": "# Prompt Lifecycle\n",
    "docs/eval_methodology.md": "# Evaluation Methodology\n",

    # examples
    "examples/sample_company_input.json": "{\n  \"name\": \"Example Company\"\n}\n",
    "examples/sample_company_overview.json": "{\n  \"profile\": \"...\"\n}\n",

    # package root
    "src/company_overview_engine/__init__.py": "# package init\n",

    # config
    "src/company_overview_engine/config/company_overview.yaml": "# company_overview config\n",
    "src/company_overview_engine/config/models.yaml": "# model routing config\n",
    "src/company_overview_engine/config/kpi_registry.py": "# KPI_REGISTRY = {...}\n",
    "src/company_overview_engine/config/kpi_packs.yaml": "# KPI packs per industry\n",
    "src/company_overview_engine/config/prompt_policies.yaml": "# prompt policies\n",
    "src/company_overview_engine/config/logging.yaml": "# logging config\n",

    # prompts
    "src/company_overview_engine/prompts/company_overview/prompt_v2025_01_10.md": "# prompt v2025_01_10\n",
    "src/company_overview_engine/prompts/company_overview/prompt_v2025_02_15.md": "# prompt v2025_02_15\n",
    "src/company_overview_engine/prompts/company_overview/meta.yaml": "# prompt metadata\n",

    # schemas
    "src/company_overview_engine/schemas/__init__.py": "# schemas init\n",
    "src/company_overview_engine/schemas/base.py": "# base Pydantic model\n",
    "src/company_overview_engine/schemas/company_overview.py": "# CompanyOverviewOutput schema\n",

    # engine
    "src/company_overview_engine/engine/llm_client.py": "# call Azure/OpenAI here\n",
    "src/company_overview_engine/engine/routing.py": "# choose model here\n",
    "src/company_overview_engine/engine/prompt_loader.py": "# load & render prompt here\n",
    "src/company_overview_engine/engine/guardrails.py": "# JSON validation / guardrails here\n",
    "src/company_overview_engine/engine/retry_policies.py": "# retry logic here\n",
    "src/company_overview_engine/engine/runtime.py": "# main company_overview() entrypoint\n",

    # eval
    "src/company_overview_engine/eval/__init__.py": "# eval init\n",
    "src/company_overview_engine/eval/datasets/company_overview.jsonl": "",
    "src/company_overview_engine/eval/metrics.py": "# eval metrics helpers\n",
    "src/company_overview_engine/eval/kpi_eval.py": "# KPI consistency checks\n",
    "src/company_overview_engine/eval/text_eval.py": "# text expectation checks\n",
    "src/company_overview_engine/eval/llm_judge.py": "# optional LLM-as-judge\n",
    "src/company_overview_engine/eval/run_tests.py": "# offline eval runner\n",

    # telemetry
    "src/company_overview_engine/telemetry/logging_config.py": "# setup logging\n",
    "src/company_overview_engine/telemetry/event_logger.py": "# log events\n",
    "src/company_overview_engine/telemetry/cost_estimator.py": "# cost estimation\n",
    "src/company_overview_engine/telemetry/exporters/console_exporter.py": "# console exporter\n",
    "src/company_overview_engine/telemetry/exporters/csv_exporter.py": "# csv exporter\n",
    "src/company_overview_engine/telemetry/exporters/prometheus_exporter.py": "# prometheus exporter\n",

    # cli
    "src/company_overview_engine/cli/__init__.py": "# cli init\n",
    "src/company_overview_engine/cli/main.py": "# CLI entrypoint\n",

    # utils
    "src/company_overview_engine/utils/json_utils.py": "# JSON helpers\n",
    "src/company_overview_engine/utils/time_utils.py": "# timing helpers\n",
    "src/company_overview_engine/utils/typing_helpers.py": "# typing helpers\n",

    # tests
    "tests/test_schema_company_overview.py": "# tests for schema\n",
    "tests/test_engine_prompt_loader.py": "# tests for prompt loader\n",
    "tests/test_engine_guardrails.py": "# tests for guardrails\n",
    "tests/test_eval_kpi_eval.py": "# tests for KPI eval\n",
    "tests/test_cli_generate.py": "# tests for CLI\n",
}


def main():
    # Create directories
    for d in DIRS:
        dir_path = PROJECT_ROOT / d
        dir_path.mkdir(parents=True, exist_ok=True)

    # Create files with minimal content
    for rel_path, content in FILES.items():
        file_path = PROJECT_ROOT / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    print(f"Created bare-bones project at: {PROJECT_ROOT.resolve()}")


if __name__ == "__main__":
    main()
