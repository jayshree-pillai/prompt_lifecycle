from typing import Any, Dict, List, Optional, Tuple


class Router:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # Section configs (your run-config YAML must include sections: ...)
        self.sections_cfg = config.get("sections", {}) or {}

        # Optional base prompt segment
        self.base_prompt_cfg = config.get("base_prompt", {}) or {}

        # Optional prompt blocks per industry (only if you use them)
        self.industries_cfg = config.get("industries", {}) or {}

        # KPI pack definitions (loaded by Runtime from kpi_packs.yaml)
        self.kpi_packs_cfg = config.get("kpi_packs", {}) or {}

        # Industry map (loaded by Runtime from industry_map.yaml)
        # Expected keys: industry_aliases, industry_map
        self.industry_map_cfg = config.get("industry_map_cfg") or config.get("industry_map") or {}

        # Prompt snippet for KPI pack (you chose KISS: prompts/kpi_pack.md)
        self.kpi_pack_prompt_cfg = config.get("kpi_pack_prompt", {}) or {"template_path": "kpi_pack.md"}

    def route(self, section: str) -> Dict[str, Any]:
        if section not in self.sections_cfg:
            available = ", ".join(sorted(self.sections_cfg.keys()))
            raise ValueError(f"Unknown section '{section}'. Available sections: {available or 'none'}")

        section_cfg = self.sections_cfg[section]

        version_key, version_cfg = self._resolve_prompt_version(section, section_cfg)

        raw_industry = section_cfg.get("industry")
        raw_sub_industry = section_cfg.get("sub_industry")

        industry = self._normalize_industry(raw_industry) if raw_industry else None
        sub_industry = raw_sub_industry  # keep original in manifest

        explicit_pack = section_cfg.get("kpi_pack")
        kpi_pack, kpi_pack_source = self._resolve_kpi_pack_kiss(
            explicit_kpi_pack=explicit_pack,
            industry=industry,
            sub_industry=raw_sub_industry,
        )

        manifest = {
            "section": section,
            "prompt_version": version_key,
            "industry": industry,
            "sub_industry": sub_industry,
            "kpi_pack": kpi_pack,
            "kpi_pack_source": kpi_pack_source,  # explicit | industry+sub | industry_default
        }

        segments: List[Dict[str, Any]] = []

        # 1) Base prompt (optional)
        base_path = self.base_prompt_cfg.get("template_path")
        if base_path:
            segments.append(
                {
                    "name": "base",
                    "template_path": base_path,
                    "variables": self.base_prompt_cfg.get("variables", {}) or {},
                }
            )

        # 2) Industry prompt block (optional)
        if industry:
            industry_cfg = self.industries_cfg.get(industry)
            if industry_cfg and industry_cfg.get("template_path"):
                segments.append(
                    {
                        "name": f"industry:{industry}",
                        "template_path": industry_cfg["template_path"],
                        "variables": industry_cfg.get("variables", {}) or {},
                    }
                )

        # 3) KPI pack prompt block (required by your design)
        kpi_ids = self._get_kpi_ids_for_pack(kpi_pack)
        kpi_segment_path = self.kpi_pack_prompt_cfg.get("template_path")
        if not kpi_segment_path:
            raise ValueError("Missing config.kpi_pack_prompt.template_path (e.g., 'kpi_pack.md')")

        segments.append(
            {
                "name": f"kpi_pack:{kpi_pack}",
                "template_path": kpi_segment_path,
                "variables": {
                    "kpi_pack_id": kpi_pack,
                    "kpi_ids_csv": ", ".join(kpi_ids),
                    "kpi_bullets": "\n".join([f"- {k}" for k in kpi_ids]),
                },
            }
        )

        # 4) Section prompt version (required)
        segments.append(
            {
                "name": f"section:{section}@{version_key}",
                "template_path": version_cfg["template_path"],
                "variables": version_cfg.get("variables", {}) or {},
            }
        )

        return {"manifest": manifest, "segments": segments}

    def _resolve_prompt_version(self, section: str, section_cfg: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        version_key = section_cfg.get("prompt_version")
        versions = section_cfg.get("prompt_versions", {}) or {}

        if not version_key:
            raise ValueError(f"Section '{section}' must define 'prompt_version'")

        version_cfg = versions.get(version_key)
        if not version_cfg:
            raise ValueError(f"Section '{section}' has no prompt_versions['{version_key}'] defined")

        if not version_cfg.get("template_path"):
            raise ValueError(f"Section '{section}' / version '{version_key}' missing 'template_path'")

        return version_key, version_cfg

    def _normalize_industry(self, industry: str) -> str:
        aliases = self.industry_map_cfg.get("industry_aliases", {}) or {}
        return aliases.get(industry, industry)

    def _normalize_sub_industry_within_industry(self, industry: str, sub_industry: str) -> str:
        imap = self.industry_map_cfg.get("industry_map", {}) or {}
        entry = imap.get(industry, {}) or {}
        aliases = entry.get("sub_industry_aliases", {}) or {}
        return aliases.get(sub_industry, sub_industry)

    def _resolve_kpi_pack_kiss(
        self,
        explicit_kpi_pack: Optional[str],
        industry: Optional[str],
        sub_industry: Optional[str],
    ) -> Tuple[str, str]:
        # #1 explicit override
        if explicit_kpi_pack:
            return explicit_kpi_pack, "explicit"

        # #3 no industry AND no explicit pack -> error
        if not industry:
            raise ValueError("No KPI pack resolution possible: provide either sections.<section>.kpi_pack or industry")

        imap = self.industry_map_cfg.get("industry_map", {}) or {}
        entry = imap.get(industry)
        if not entry:
            raise ValueError(f"Industry '{industry}' not found in industry_map.yaml")

        # #2 industry + sub_industry mapping
        if sub_industry:
            normalized_sub = self._normalize_sub_industry_within_industry(industry, sub_industry)
            sub_map = entry.get("sub_industries", {}) or {}
            if normalized_sub in sub_map:
                return sub_map[normalized_sub], "industry+sub"

        # #2 industry default
        default_pack = entry.get("default_kpi_pack")
        if default_pack:
            return default_pack, "industry_default"

        raise ValueError(f"Industry '{industry}' has no default_kpi_pack and no sub_industry match")

    def _get_kpi_ids_for_pack(self, kpi_pack_id: str) -> List[str]:
        if not isinstance(self.kpi_packs_cfg, dict) or not self.kpi_packs_cfg:
            raise ValueError("config['kpi_packs'] is missing/empty. Did Runtime load kpi_packs_file?")

        pack = self.kpi_packs_cfg.get(kpi_pack_id)
        if not pack:
            raise ValueError(f"KPI pack '{kpi_pack_id}' not found in config['kpi_packs']")

        kpi_ids = pack.get("kpi_ids", []) or []
        if not isinstance(kpi_ids, list) or not kpi_ids:
            raise ValueError(f"KPI pack '{kpi_pack_id}' has empty/invalid 'kpi_ids'")

        return kpi_ids
