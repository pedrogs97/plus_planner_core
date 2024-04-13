"""Invoke tasks for the project"""

from invoke import task


@task
def rundev(cmd):
    """Run the development server with uvicorn."""
    cmd.run("uvicorn src.main:appAPI --port 8000 --reload")
