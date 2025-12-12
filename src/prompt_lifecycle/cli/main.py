import argparse
import json
from prompt_lifecycle.engine.runtime import Runtime


def parse_args():
    parser = argparse.ArgumentParser(description="Prompt Lifecycle CLI")

    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to YAML config for this run",
    )

    parser.add_argument(
        "--section",
        type=str,
        required=True,
        help="Which report section to generate (e.g., company_overview)",
    )

    parser.add_argument(
        "--prompt-only",
        action="store_true",
        help="Print only the assembled prompt text (no manifest, no output wrapper).",
    )

    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Print only the prompt manifest JSON (no prompt text).",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    runtime = Runtime(config_path=args.config)

    # If you want prompt-only or manifest-only, we bypass the pretty wrapper
    if args.prompt_only or args.manifest_only:
        prompt_spec = runtime.router.route(args.section)
        assembled_prompt, assembly_manifest = runtime.prompt_loader.load(prompt_spec)

        if args.manifest_only:
            print(json.dumps(assembly_manifest, indent=2))
            return

        # prompt_only
        print(assembled_prompt)
        return

    # Default: full output (manifest + prompt + stub output)
    result = runtime.run(section=args.section)
    print(result)


if __name__ == "__main__":
    main()
