import asyncio
import sys
from pathlib import Path
from typing import Optional, List
import typer
import logging

from pipeline.processor import DocumentProcessor
from pipeline.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="docushield-cli",
    help="DocuShield AI Command Line Interface for batch document redaction"
)

@app.command()
def redact(
    input_path: str = typer.Argument(..., help="Input file or directory path"),
    output_dir: str = typer.Option("output", "--out", "-o", help="Output directory"),
    policy_file: str = typer.Option("configs/policies.yaml", "--policy", "-p", help="Policy configuration file"),
    audit_file: Optional[str] = typer.Option(None, "--audit", "-a", help="Audit log output file"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Process directories recursively"),
    config_file: str = typer.Option("configs/default.yaml", "--config", "-c", help="Configuration file")
):
    """Redact PII from documents"""
    asyncio.run(_redact_documents(
        input_path, output_dir, policy_file, audit_file, recursive, config_file
    ))

async def _redact_documents(
    input_path: str, 
    output_dir: str, 
    policy_file: str, 
    audit_file: Optional[str], 
    recursive: bool,
    config_file: str
):
    """Async function to redact documents"""
    try:
        # Load configuration
        config = Config.load(config_file)
        processor = DocumentProcessor(config)
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Get input files
        input_path_obj = Path(input_path)
        files_to_process = []
        
        if input_path_obj.is_file():
            files_to_process = [input_path_obj]
        elif input_path_obj.is_dir():
            pattern = "**/*" if recursive else "*"
            extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff']
            
            for ext in extensions:
                files_to_process.extend(input_path_obj.glob(f"{pattern}{ext}"))
                files_to_process.extend(input_path_obj.glob(f"{pattern}{ext.upper()}"))
        else:
            typer.echo(f"Error: Input path {input_path} does not exist", err=True)
            sys.exit(1)
        
        if not files_to_process:
            typer.echo("No supported files found to process", err=True)
            sys.exit(1)
        
        typer.echo(f"Found {len(files_to_process)} files to process")
        
        all_audit_entries = []
        
        # Process each file
        for file_path in files_to_process:
            try:
                typer.echo(f"Processing: {file_path}")
                
                result = await processor.process_document(str(file_path), file_path.name)
                
                # Copy output file to output directory
                output_filename = f"redacted_{file_path.name}"
                final_output_path = Path(output_dir) / output_filename
                
                # Move the processed file
                import shutil
                shutil.move(result.output_path, str(final_output_path))
                
                typer.echo(f"  -> Saved: {final_output_path}")
                typer.echo(f"  -> Found {result.detections_count} PII items")
                
                # Collect audit entries
                all_audit_entries.extend(result.audit_entries)
                
            except Exception as e:
                typer.echo(f"Error processing {file_path}: {str(e)}", err=True)
                continue
        
        # Save audit log if requested
        if audit_file:
            import json
            with open(audit_file, 'w') as f:
                json.dump([entry.__dict__ for entry in all_audit_entries], f, indent=2)
            typer.echo(f"Audit log saved: {audit_file}")
        
        typer.echo(f"Processing complete. {len(files_to_process)} files processed.")
        
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@app.command()
def health():
    """Check system health"""
    try:
        # Check if models directory exists
        models_path = Path("models")
        if not models_path.exists():
            typer.echo("⚠️  Models directory not found", err=True)
            return
        
        # Check configuration files
        config_path = Path("configs")
        if not config_path.exists():
            typer.echo("⚠️  Configuration directory not found", err=True)
            return
        
        typer.echo("✅ DocuShield AI CLI is healthy")
        
    except Exception as e:
        typer.echo(f"❌ Health check failed: {str(e)}", err=True)

if __name__ == "__main__":
    app()