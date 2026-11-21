"""
Streamlit Community Cloud default entrypoint for ChillGPT.
Runs the unified ChillGPT application (Part 1 + Part 2).
"""
import runpy

if __name__ == "__main__":
    runpy.run_module("app", run_name="__main__")
else:
    import app
