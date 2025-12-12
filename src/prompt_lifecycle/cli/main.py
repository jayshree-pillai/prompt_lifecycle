import argparse
import json

from prompt_lifecycle.engine.runtime import Runtime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prompt Lifecycle CLI")

    parser.add_argument(
        "--config",
        required=True,
        help="Path to the run-config YAML (e.g., src/prompt_lifecycle/config/company_overview.yaml)",
    )
    parser.add_argument(
        "--section",
        required=True,
        help="Section key under config.sections (e.g., company_overview)",
    )

    # Optional runtime overrides (lets you experiment without editing YAML)
    parser.add_argument("--industry", help="Override industry (e.g., ENERGY)")
    parser.add_argument(
        "--sub-industry",
        dest="sub_industry",
        help="Override sub-industry (e.g., 4.1 Upstream/Services)",
    )
    parser.add_argument(
        "--prompt-version",
        dest="prompt_version",
        help="Override prompt version key (e.g., v2025_01_10)",
    )
    parser.add_argument(
        "--kpi-pack",
        dest="kpi_pack",
        help="Override KPI pack id directly (e.g., ENERGY__Upstream_Services)",
    )

    # Output modes
    parser.add_argument(
        "--prompt-only",
        action="store_true",
        help="Print only the assembled prompt text.",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Print only the assembly manifest (JSON).",
    )

    return parser


def collect_overrides(args: argparse.Namespace) -> dict:
    return {
        "section": args.section,
        "industry": args.industry,
        "sub_industry": args.sub_industry,
        "prompt_version": args.prompt_version,
        "kpi_pack": args.kpi_pack,
    }


def main() -> None:
    args = build_parser().parse_args()

    runtime = Runtime(config_path=args.config, overrides=collect_overrides(args))

    # Lightweight modes for debugging / inspection
    if args.prompt_only or args.manifest_only:
        prompt_spec = runtime.router.route(args.section)
        prompt_text, manifest = runtime.prompt_loader.load(prompt_spec)

        if args.manifest_only:
            print(json.dumps(manifest, indent=2))
        else:
            print(prompt_text)
        return

    # Default: full run (includes stub LLM output)
    print(runtime.run(section=args.section))


if __name__ == "__main__":
    main()
