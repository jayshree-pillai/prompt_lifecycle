import os
from typing import Any, Dict, List, Tuple


class PromptLoader:
    """
    Loads prompt templates from disk, renders variables, and assembles the final prompt.

    Input contract (prompt_spec) expected from Router:
      {
        "manifest": {...},
        "segments": [
          {"name": str, "template_path": str, "variables": dict},
          ...
        ]
      }

    Output contract:
      (assembled_prompt_text, assembly_manifest)

    Where assembly_manifest includes:
      - router_manifest (industry, kpi_pack, version, etc.)
      - ordered list of segments with resolved absolute/relative paths
    """

    def __init__(self, config: Dict[str, Any]):
        prompts_cfg = config.get("prompts", {})
        self.base_dir = prompts_cfg.get("base_dir", "config/prompts")

    def _resolve_path(self, template_path: str) -> str:
        if os.path.isabs(template_path):
            return template_path
        return os.path.join(self.base_dir, template_path)

    def _render_template(self, resolved_path: str, variables: Dict[str, Any]) -> str:
        with open(resolved_path, "r", encoding="utf-8") as f:
            template = f.read()

        try:
            return template.format(**variables)
        except KeyError as exc:
            # KeyError prints like: KeyError('company_name')
            missing = str(exc).strip("'")
            raise KeyError(
                f"Missing variable '{missing}' for template: {resolved_path}"
            )

    def load(self, prompt_spec: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        segments: List[Dict[str, Any]] = prompt_spec.get("segments", [])
        if not segments:
            raise ValueError("prompt_spec must include non-empty 'segments'")

        router_manifest = prompt_spec.get("manifest", {})

        rendered_parts: List[str] = []
        segment_manifest: List[Dict[str, Any]] = []

        for seg in segments:
            name = seg.get("name", "unnamed")
            template_path = seg.get("template_path")
            if not template_path:
                raise ValueError(f"Segment '{name}' is missing 'template_path'")

            variables = seg.get("variables", {})

            resolved = self._resolve_path(template_path)
            text = self._render_template(resolved, variables)

            rendered_parts.append(text)
            segment_manifest.append(
                {
                    "name": name,
                    "template_path": template_path,
                    "resolved_path": resolved,
                    "variables_keys": sorted(list(variables.keys())),
                    "chars": len(text),
                }
            )

        assembled = "\n\n".join(rendered_parts)

        assembly_manifest = {
            "router_manifest": router_manifest,
            "segments": segment_manifest,
            "assembled_chars": len(assembled),
        }

        return assembled, assembly_manifest
