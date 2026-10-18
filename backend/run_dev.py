import os
import uvicorn

if __name__ == "__main__":
    current_env = os.getenv("APP_ENV", "local")
    print(f"[*] Menjalankan dev watcher untuk lingkungan: {current_env}")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7000,
        reload=True,
        # Direktori yang dipantau
        reload_dirs=["app"],
        # Ekstensi file yang memicu restart otomatis (termasuk file env & rego)
        reload_includes=[
            "*.env",
            ".env.*",
            "*.rego",
            "*.json",
            "*.yaml",
            "*.py"
        ],
        reload_delay=0.5,
    )