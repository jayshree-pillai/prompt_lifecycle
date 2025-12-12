import os
import json
import yaml
from typing import Any, Dict, Optional

from prompt_lifecycle.engine.routing import Router
from prompt_lifecycle.engine.prompt_loader import PromptLoader
from prompt_lifecycle.engine.llm_client import LLMClient

class Runtime:
    def __init__(self, config_path: str, overrides: Optional[Dict[str, Any]] = None):
        self.config_path = config_path
        self.config_dir = os.path.dirname(os.path.abspath(config_path))

        self.config = self._load_config(config_path)
        self._hydrate_external_configs()

        if overrides:
            self._apply_overrides(overrides)

        self.router = Router(self.config)
        self.prompt_loader = PromptLoader(self.config)
        self.llm = LLMClient(self.config)

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
        industry_map_file = self.config.get("industry_map_file")
        if industry_map_file:
            industry_map_cfg = self._load_yaml_file(industry_map_file)
            self.config["industry_map_cfg"] = {
                "industry_aliases": industry_map_cfg.get("industry_aliases", {}) or {},
                "industry_map": industry_map_cfg.get("industry_map", {}) or {},
            }

        kpi_packs_file = self.config.get("kpi_packs_file")
        if kpi_packs_file:
            kpi_packs_cfg = self._load_yaml_file(kpi_packs_file)
            packs = kpi_packs_cfg.get("kpi_packs", {})
            if not isinstance(packs, dict):
                raise ValueError("kpi_packs.yaml must contain a top-level 'kpi_packs:' mapping")
            self.config["kpi_packs"] = packs

    def _apply_overrides(self, overrides: Dict[str, Any]) -> None:
        """
        Applies CLI overrides to one section config before Router is built.
        Expected keys: section (required), industry, sub_industry, prompt_version, kpi_pack
        """
        section = overrides.get("section")
        if not section:
            raise ValueError("Runtime overrides must include 'section'")

        sections = self.config.get("sections", {}) or {}
        if section not in sections:
            raise ValueError(f"Unknown section '{section}' in config. Available: {', '.join(sorted(sections.keys()))}")

        scfg = sections[section]

        if overrides.get("industry") is not None:
            scfg["industry"] = overrides["industry"]

        if overrides.get("sub_industry") is not None:
            scfg["sub_industry"] = overrides["sub_industry"]

        if overrides.get("kpi_pack") is not None:
            scfg["kpi_pack"] = overrides["kpi_pack"]

        if overrides.get("prompt_version") is not None:
            pv = overrides["prompt_version"]
            pvers = scfg.get("prompt_versions", {}) or {}
            if pv not in pvers:
                raise ValueError(
                    f"prompt_version '{pv}' not defined for section '{section}'. "
                    f"Available: {', '.join(sorted(pvers.keys()))}"
                )
            scfg["prompt_version"] = pv

        self.config["sections"] = sections

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
