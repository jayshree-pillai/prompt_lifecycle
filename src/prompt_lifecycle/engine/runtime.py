import os
import json
import yaml
from typing import Any, Dict, Tuple

from prompt_lifecycle.engine.routing import Router
from prompt_lifecycle.engine.prompt_loader import PromptLoader
from prompt_lifecycle.engine.llm_client import LLMClient


class Runtime:
    """
    Runtime orchestrator:
    - Loads run config YAML
    - Hydrates config by loading referenced YAML files (industry_map, kpi_packs)
    - Router selects segments
    - PromptLoader assembles prompt + manifest
    - LLMClient called (stub echoes today)
    """

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config_dir = os.path.dirname(os.path.abspath(config_path))

        self.config = self._load_config(config_path)
        self._hydrate_external_configs()

        self.router = Router(self.config)
        self.prompt_loader = PromptLoader(self.config)
        self.llm = LLMClient(self.config)

    # -----------------------
    # Config loading
    # -----------------------
    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _resolve_path(self, maybe_path: str) -> str:
        if os.path.isabs(maybe_path):
            return maybe_path
        return os.path.join(self.config_dir, maybe_path)

    def _load_yaml_file(self, path: str) -> Dict[str, Any]:
        resolved = self._resolve_path(path)
        with open(resolved, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _hydrate_external_configs(self) -> None:
        """
        Loads external YAMLs referenced by the run-config and injects them into self.config
        so Router can use them directly.
        """
        # 1) industry_map.yaml
        industry_map_file = self.config.get("industry_map_file")
        if industry_map_file:
            industry_map_cfg = self._load_yaml_file(industry_map_file)

            # Keep only what Router needs (KISS)
            self.config["industry_map_cfg"] = {
                "industry_aliases": industry_map_cfg.get("industry_aliases", {}) or {},
                "industry_map": industry_map_cfg.get("industry_map", {}) or {},
            }

        # 2) kpi_packs.yaml
        kpi_packs_file = self.config.get("kpi_packs_file")
        if kpi_packs_file:
            kpi_packs_cfg = self._load_yaml_file(kpi_packs_file)

            packs = kpi_packs_cfg.get("kpi_packs", {})
            if not isinstance(packs, dict):
                raise ValueError("kpi_packs.yaml must contain a top-level 'kpi_packs:' mapping")

            self.config["kpi_packs"] = packs

    # -----------------------
    # Run
    # -----------------------
    def run(self, section: str) -> str:
        prompt_spec = self.router.route(section)
        assembled_prompt, assembly_manifest = self.prompt_loader.load(prompt_spec)

        llm_output = self.llm.call(assembled_prompt)

        return (
            "===== PROMPT MANIFEST =====\n"
            f"{json.dumps(assembly_manifest, indent=2)}\n\n"
            "===== ASSEMBLED PROMPT TEXT =====\n"
            f"{assembled_prompt}\n\n"
            "===== LLM OUTPUT (stub today) =====\n"
            f"{llm_output}\n"
        )
