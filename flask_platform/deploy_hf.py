import os
import re
import sys
import time
import argparse
from huggingface_hub import HfApi, whoami

REPO_ID = "egyx/hydroflow-water-segmentation"
SPACE_URL = f"https://huggingface.co/spaces/{REPO_ID}"
MODEL_URL = f"https://huggingface.co/{REPO_ID}"


def _update_readme_sdk(base_dir: str, target_sdk: str):
    """Updates the YAML frontmatter in README.md to match the active Space SDK."""
    readme_path = os.path.join(base_dir, "README.md")
    if not os.path.exists(readme_path):
        return
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"^(sdk:\s*)([a-zA-Z0-9_-]+)",
        rf"\g<1>{target_sdk}",
        content,
        flags=re.MULTILINE
    )
    if "full_width:" not in new_content:
        new_content = re.sub(r"(license:\s*[a-zA-Z0-9_-]+)", r"\1\nfull_width: true", new_content)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def deploy(mode: str = "auto", upload_model: bool = True):
    print("=" * 70)
    print(" HydroFlow Water Segmentation - Hugging Face Deployment Pipeline")
    print("=" * 70)

    api = HfApi()

    # Step 1: Verify Authentication
    try:
        user_info = whoami()
        username = user_info.get("name", "unknown")
        is_pro = user_info.get("isPro", False)
        print(f"[1/4] Authenticated User: @{username} (HF Pro: {is_pro})")
    except Exception as e:
        print(f"[!] Hugging Face authentication failed: {e}")
        sys.exit(1)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Step 2: Initialize Space Repository
    active_sdk = "docker" if mode == "docker" else ("static" if mode == "static" else "docker")
    space_created = False

    if mode in ("docker", "auto"):
        print(f"[2/4] Attempting to create Space: {REPO_ID} (SDK: docker)...")
        try:
            api.create_repo(
                repo_id=REPO_ID,
                repo_type="space",
                space_sdk="docker",
                exist_ok=True
            )
            active_sdk = "docker"
            space_created = True
            print(f"      Docker Space repository ready at: {SPACE_URL}")
        except Exception as e:
            err_msg = str(e)
            if "402" in err_msg or "Payment Required" in err_msg:
                print("\n" + "-" * 70)
                print(" [NOTICE] Hugging Face Policy: Hosting new Docker Spaces on free")
                print(" accounts requires a PRO subscription ($9/mo).")
                print(" Falling back to Space SDK: static for instant zero-cost hosting.")
                print("-" * 70 + "\n")
                if mode == "docker":
                    print("[!] Mode was explicitly set to 'docker'. Halting per user flag.")
                    sys.exit(402)
                # Automatically adapt to static space
                active_sdk = "static"
            else:
                print(f"[!] Error creating Space: {err_msg}")
                sys.exit(1)

    if not space_created and active_sdk == "static":
        print(f"[2/4] Initializing Hugging Face Space: {REPO_ID} (SDK: static)...")
        try:
            api.create_repo(
                repo_id=REPO_ID,
                repo_type="space",
                space_sdk="static",
                exist_ok=True
            )
            print(f"      Static Space repository ready at: {SPACE_URL}")
        except Exception as e:
            print(f"[!] Error creating Static Space: {e}")
            sys.exit(1)

    # Sync README frontmatter sdk to match target
    _update_readme_sdk(base_dir, active_sdk)

    # Step 3: Upload Space files
    print(f"[3/4] Uploading platform contents to Space ({active_sdk} mode)...")
    print("      (Including ONNX model, PyTorch weights, Dockerfile, and web dashboard)")

    ignore_patterns = [
        "**/__pycache__/**",
        "**/.git/**",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        "**/.pytest_cache/**",
        ".env",
        ".venv"
    ]

    t0 = time.perf_counter()
    commit_info = api.upload_folder(
        repo_id=REPO_ID,
        repo_type="space",
        folder_path=base_dir,
        commit_message=f"Deploy HydroFlow Water Segmentation Platform v2.0 ({active_sdk.capitalize()} + ONNX)",
        ignore_patterns=ignore_patterns
    )
    elapsed = time.perf_counter() - t0
    commit_hash = commit_info.oid if hasattr(commit_info, "oid") else str(commit_info)
    print(f"      Space upload complete in {elapsed:.2f}s! Commit: {commit_hash[:10] if len(commit_hash) >= 10 else commit_hash}")

    # Optional / Secondary: Upload to Model Hub for open-source model registry
    if upload_model:
        print("\n[*] Publishing model assets to Hugging Face Model Hub...")
        try:
            api.create_repo(
                repo_id=REPO_ID,
                repo_type="model",
                exist_ok=True
            )
            model_commit = api.upload_folder(
                repo_id=REPO_ID,
                repo_type="model",
                folder_path=base_dir,
                commit_message="Publish HydroFlow ResNet-34 12-Channel U-Net Weights & ONNX Artifacts",
                ignore_patterns=ignore_patterns
            )
            print(f"    Model Hub published at: {MODEL_URL}")
        except Exception as e:
            print(f"    Notice: Model Hub upload skipped: {e}")

    # Step 4: Verification
    print(f"\n[4/4] Verifying Space runtime status...")
    try:
        runtime = api.get_space_runtime(repo_id=REPO_ID)
        domains = runtime.raw.get('domains', [{}]) if hasattr(runtime, 'raw') and runtime.raw else []
        default_subdomain = REPO_ID.replace('/', '-')
        default_domain = f"{default_subdomain}.static.hf.space" if active_sdk == "static" else f"{default_subdomain}.hf.space"
        live_domain = domains[0].get('domain', default_domain) if domains and domains[0].get('domain') else default_domain
        print(f"      Current Stage:    {runtime.stage}")
        print(f"      Hardware:         {runtime.hardware or 'static'}")
        print(f"      Live Domain URL:  https://{live_domain}")
    except Exception as e:
        print(f"      Runtime status check: {e}")

    print("=" * 70)
    print(" DEPLOYMENT COMPLETE SUCCESSFULLY!")
    print(f" Live Space URL: {SPACE_URL}")
    if upload_model:
        print(f" Model Hub URL:  {MODEL_URL}")
    print("=" * 70)
    return SPACE_URL


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy HydroFlow to Hugging Face")
    parser.add_argument(
        "--mode",
        choices=["auto", "docker", "static"],
        default="auto",
        help="Deployment mode: 'auto' (tries docker, falls back to static if non-Pro), 'docker', 'static'"
    )
    parser.add_argument(
        "--no-model",
        action="store_true",
        help="Do not publish to Model Hub alongside Space"
    )
    args = parser.parse_args()
    deploy(mode=args.mode, upload_model=not args.no_model)
