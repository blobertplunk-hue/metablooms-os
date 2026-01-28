# ESLint Sensor Runner (STUB)
# This runner expects ESLint to be available in the execution environment.
# It DOES NOT install ESLint.

def run_eslint(target_path, output_json):
    raise RuntimeError(
        "ESLint binary not available in sandbox. "
        "Provide eslint externally or run in CI."
    )
