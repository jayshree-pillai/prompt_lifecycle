import os
from typing import Any, Dict, List, Tuple


class PromptLoader:
    """
    Reads prompt templates from disk and stitches them into one final prompt.

    Router hands us a list of segments like:
      [{"name": "...", "template_path": "...", "variables": {...}}, ...]

    We return:
      (assembled_prompt_text, manifest)
    """

    def __init__(self, config: Dict[str, Any]):
        prompts_cfg = config.get("prompts", {}) or {}
        self.base_dir = prompts_cfg.get("base_dir", "config/prompts")

    def _resolve(self, template_path: str) -> str:
        return template_path if os.path.isabs(template_path) else os.path.join(self.base_dir, template_path)

    def _read(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _render(self, template_text: str, variables: Dict[str, Any], resolved_path: str) -> str:
        try:
            return template_text.format(**variables)
        except KeyError as exc:
            missing = str(exc).strip("'")
            raise KeyError(f"Template is missing variable '{missing}': {resolved_path}") from None

    def load(self, prompt_spec: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        segments: List[Dict[str, Any]] = prompt_spec.get("segments", []) or []
        if not segments:
            raise ValueError("prompt_spec.segments is required and cannot be empty")

        router_manifest = prompt_spec.get("manifest", {}) or {}

        rendered_parts: List[str] = []
        seg_manifest: List[Dict[str, Any]] = []

        for seg in segments:
            name = seg.get("name") or "unnamed"
            template_path = seg.get("template_path")
            if not template_path:
                raise ValueError(f"Segment '{name}' is missing template_path")

            variables = seg.get("variables", {}) or {}

            resolved_path = self._resolve(template_path)
            template_text = self._read(resolved_path)
            text = self._render(template_text, variables, resolved_path)

            rendered_parts.append(text)
            seg_manifest.append(
                {
                    "name": name,
                    "template_path": template_path,
                    "resolved_path": resolved_path,
                    "variables_keys": sorted(variables.keys()),
                    "chars": len(text),
                }
            )

        assembled = "\n\n".join(rendered_parts)

        manifest = {
            "router_manifest": router_manifest,
            "segments": seg_manifest,
            "assembled_chars": len(assembled),
        }

        return assembled, manifest
