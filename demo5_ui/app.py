import os
import subprocess
import logging
import shutil # Added for directory deletion
import sys # Added sys import
from pathlib import Path
from datetime import datetime # Added for timestamp formatting
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, abort, jsonify, Response # Added jsonify and Response
from markupsafe import escape # For safely displaying paths
from werkzeug.utils import safe_join # For safe path joining
from markdown import markdown

# Need BaseBot for the new route
# --- Path Setup --- #
SCRIPT_DIR_APP = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR_APP.parent # Assumes demo5_ui is at the root
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# --- End Path Setup --- #
from core_components.base_bot import BaseBot, DEFAULT_JOURNAL_FILENAME

# --- Configuration ---
# Assuming this script runs from the 'demo5_ui' directory
CORE_COMPONENTS_DIR = PROJECT_ROOT / "core_components"
DEMO5_SCRIPT_PATH = CORE_COMPONENTS_DIR / "demo5.py"
DEMO5_OUTPUT_DIR = CORE_COMPONENTS_DIR / "demo5_output"

# Check if paths exist (basic validation)
if not DEMO5_SCRIPT_PATH.is_file():
    raise FileNotFoundError(f"Demo script not found: {DEMO5_SCRIPT_PATH}")
if not CORE_COMPONENTS_DIR.is_dir():
    raise FileNotFoundError(f"Core components directory not found: {CORE_COMPONENTS_DIR}")
# Output dir might not exist yet, demo5.py creates it

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = os.urandom(24) # Needed for flash messages
logging.basicConfig(level=logging.INFO) # Basic logging for the Flask app

# --- Helper Functions ---
def get_run_ids():
    """Lists available runs based on directory names in demo5_output.

    Returns:
        list: A list of dictionaries, each with 'id' (raw), 'formatted_ts',
              and 'is_ai_task' (boolean). Sorted descending by time.
    """
    runs_data = []
    if DEMO5_OUTPUT_DIR.is_dir():
        for item in DEMO5_OUTPUT_DIR.iterdir():
            if item.is_dir() and item.name.startswith("run_"):
                run_id_raw = item.name.replace("run_", "")
                is_ai_task = False
                parse_id = run_id_raw

                # Check for and strip the AI task suffix before parsing
                if run_id_raw.endswith("_ai_task"):
                    is_ai_task = True
                    # Use removesuffix if available (Python 3.9+), else slice
                    try: parse_id = run_id_raw.removesuffix("_ai_task")
                    except AttributeError: parse_id = run_id_raw[:-len("_ai_task")] # Fallback

                formatted_time = "Invalid Timestamp"
                try:
                    # Attempt to parse the timestamp string (without suffix)
                    dt_object = datetime.strptime(parse_id, "%Y%m%d_%H%M%S_%f")
                    formatted_time = dt_object.strftime("%B %d, %Y - %I:%M:%S") + f".{dt_object.microsecond // 1000:03d} " + dt_object.strftime("%p")
                except ValueError:
                    logging.warning(f"Could not parse run ID part as timestamp: {parse_id} (from raw {run_id_raw})")
                    formatted_time = run_id_raw # Fallback to raw ID

                runs_data.append({
                    'id': run_id_raw, # Use the original raw ID for links/deletion
                    'formatted_ts': formatted_time,
                    'is_ai_task': is_ai_task
                })

    # Sort by the original timestamp string descending (newest first)
    runs_data.sort(key=lambda x: x['id'], reverse=True)
    return runs_data

def get_report_content_html(run_id):
    """Reads the summary report for a given run_id and converts it to HTML."""
    report_path = DEMO5_OUTPUT_DIR / f"run_{run_id}" / "summary_report.md"
    if report_path.is_file():
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            # Basic markdown conversion
            html_content = markdown(md_content)
            return html_content
        except Exception as e:
            logging.error(f"Error reading or converting report {report_path}: {e}")
            return f"<p>Error reading report file: {e}</p>"
    else:
        return "<p>Summary report not found for this run.</p>"

# --- Routes ---
@app.route('/')
def index():
    """Main page: lists runs and allows triggering a new run."""
    all_runs = get_run_ids()
    latest_run = None
    historical_runs = []

    if all_runs:
        latest_run = all_runs[0]
        historical_runs = all_runs[1:]

    return render_template(
        'index.html',
        latest_run=latest_run,
        historical_runs=historical_runs
    )

@app.route('/run', methods=['POST'])
def run_demo():
    """Triggers the demo5.py script and returns JSON status."""
    logging.info("Received request to run demo5.py (AJAX)")
    status = 'error'
    message = 'An unexpected error occurred.'
    try:
        process = subprocess.run(
            ['python', str(DEMO5_SCRIPT_PATH)],
            capture_output=True,
            text=True,
            check=True,
            cwd=PROJECT_ROOT
        )
        log_stdout = f"Stdout: {process.stdout[:200]}..." if process.stdout else "No stdout."
        log_stderr = f"Stderr: {process.stderr[:200]}..." if process.stderr else "No stderr."
        logging.info(f"demo5.py ran successfully. {log_stdout} {log_stderr}")
        status = 'success'
        message = f"Demo run completed successfully! {log_stderr if process.stderr else ''}"
        # Note: Stderr might contain warnings, still considered success if exit code is 0

    except FileNotFoundError:
        error_msg = "Error: 'python' command not found or script path incorrect."
        logging.error(error_msg)
        message = error_msg
    except subprocess.CalledProcessError as e:
        error_msg = f"Error running demo5.py (Exit Code {e.returncode}): {e.stderr[:200]}..."
        logging.error(error_msg)
        message = error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred during script execution: {e}"
        logging.error(error_msg)
        message = error_msg

    return jsonify({'status': status, 'message': message})

@app.route('/run_task', methods=['POST'])
def run_task():
    """Initiates an AI Nova task run, saves the task, and returns run_id.
    The actual processing and streaming happens via /stream_task/<run_id>.
    """
    task_input = request.form.get('task_input')
    model_name = 'llama3' # Keep hardcoded for now

    if not task_input:
        return jsonify({'status': 'error', 'message': 'Task input cannot be empty.'}), 400

    logging.info(f"Received request to INITIATE AI task: {task_input[:50]}... using model {model_name}")

    # --- Create a unique run environment --- #
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + "_ai_task"
    run_dir = DEMO5_OUTPUT_DIR / f"run_{run_id}"
    status = 'error'
    message = 'An unexpected error occurred creating the AI task run.'

    try:
        run_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created run directory for AI task: {run_dir}")

        # --- Save task input for the streaming endpoint --- #
        task_file_path = run_dir / "input_task.txt"
        with open(task_file_path, 'w', encoding='utf-8') as f:
            f.write(task_input)
        logging.info(f"Saved task input to {task_file_path}")

        # --- Instantiate Bot only to ensure paths/client are ready (optional?) ---
        # Or we can instantiate it fresh in the stream endpoint
        bot_base_path = run_dir / "bot_files"
        try:
            # We create it here to potentially catch init errors early
            ai_bot = BaseBot(base_path=bot_base_path)
            logging.info(f"Pre-instantiated bot {ai_bot.bot_id} for task run {run_id}.")
            # Log initial journal entry
            ai_bot.log_action(f"AI Task Run Initialized (Pending Stream).\nRun ID: {run_id}\nModel: {model_name}", filename=DEFAULT_JOURNAL_FILENAME)
        except Exception as bot_init_err:
             logging.error(f"Failed to pre-instantiate bot for run {run_id}: {bot_init_err}")
             # Still allow proceeding, stream endpoint will try again / fail
             pass # Consider if this should be a hard failure

        status = 'pending'
        message = f'AI task run {run_id} initiated. Waiting for stream connection.'

    except Exception as e:
        error_msg = f"Error setting up AI task run {run_id}: {e}"
        logging.exception(error_msg)
        message = error_msg
        # Cannot return run_id if setup failed fundamentally
        return jsonify({'status': 'error', 'message': message}), 500

    # Return pending status and the run_id for the client to connect to the stream
    return jsonify({'status': status, 'message': message, 'run_id': run_id})

@app.route('/report/<run_id>')
def view_report(run_id):
    """Displays the summary report for a specific run."""
    logging.info(f"Request to view report for run_id: {run_id}")
    report_html = get_report_content_html(run_id)
    return render_template('report.html', run_id=run_id, report_content=report_html)

@app.route('/delete/<run_id>', methods=['POST'])
def delete_run(run_id):
    """Deletes the specified run directory."""
    logging.info(f"Request to delete run_id: {run_id}")
    run_dir_path = DEMO5_OUTPUT_DIR / f"run_{run_id}"

    if not run_dir_path.is_dir():
        logging.warning(f"Attempted to delete non-existent directory: {run_dir_path}")
        flash(f"Run directory for {run_id} not found.", "warning")
        return redirect(url_for('index'))

    try:
        shutil.rmtree(run_dir_path)
        logging.info(f"Successfully deleted directory: {run_dir_path}")
        flash(f"Successfully deleted run {run_id}.", "success")
    except OSError as e:
        logging.error(f"Error deleting directory {run_dir_path}: {e}")
        flash(f"Error deleting run {run_id}: {e}", "danger")
    except Exception as e:
        logging.error(f"Unexpected error deleting directory {run_dir_path}: {e}")
        flash(f"Unexpected error deleting run {run_id}: {e}", "danger")

    return redirect(url_for('index'))

@app.route('/explore/<run_id>/')
@app.route('/explore/<run_id>/<path:sub_path>')
def explore_run_files(run_id, sub_path='.'):
    """Allows browsing files within a specific run directory."""
    logging.info(f"Exploring run {run_id}, path: {sub_path}")
    base_run_path = DEMO5_OUTPUT_DIR / f"run_{run_id}"

    # --- Security: Prevent directory traversal --- #
    try:
        # Ensure the base run directory exists
        if not base_run_path.is_dir():
            logging.error(f"Base run directory not found: {base_run_path}")
            flash(f"Run {run_id} not found.", "danger")
            return redirect(url_for('index'))

        # Safely join the base path and the requested sub-path
        target_path = Path(safe_join(str(base_run_path.resolve()), sub_path)).resolve()

        # Crucial check: Ensure the resolved target path is still within the base run path
        if not str(target_path).startswith(str(base_run_path.resolve())):
            logging.warning(f"Directory traversal attempt blocked: {run_id} / {sub_path}")
            abort(404) # Or return a permission denied error

    except Exception as e:
        logging.error(f"Path safety check error for {run_id}/{sub_path}: {e}")
        abort(500)
    # --- End Security --- #

    if not target_path.exists():
        logging.warning(f"Target path does not exist: {target_path}")
        abort(404)

    # Generate breadcrumbs
    relative_path = target_path.relative_to(base_run_path)
    breadcrumbs = [(url_for('explore_run_files', run_id=run_id, sub_path='.'), ".")]
    current_crumb_path = Path('.')
    for part in relative_path.parts:
        if part == '.': continue
        current_crumb_path = current_crumb_path / part
        breadcrumbs.append((url_for('explore_run_files', run_id=run_id, sub_path=str(current_crumb_path)), part))

    items = []
    file_content = None
    is_directory = target_path.is_dir()
    file_download_url = None # Initialize download URL

    if is_directory:
        try:
            for item in sorted(target_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                item_rel_path = item.relative_to(base_run_path)
                items.append({
                    'name': item.name,
                    'path': str(item_rel_path),
                    'is_dir': item.is_dir(),
                    'url': url_for('explore_run_files', run_id=run_id, sub_path=str(item_rel_path))
                })
        except OSError as e:
            logging.error(f"Error listing directory {target_path}: {e}")
            flash(f"Could not list directory contents: {e}", "warning")
            # Allow rendering the page but show empty list
    else: # It's a file
        file_download_url = url_for('download_run_file', run_id=run_id, sub_path=str(relative_path))
        try:
            # Simple text file rendering for now
            # Limit reading size for safety/performance?
            with open(target_path, 'r', encoding='utf-8', errors='replace') as f:
                file_content = f.read() # Read entire file for now
        except Exception as e:
            logging.error(f"Error reading file {target_path}: {e}")
            flash(f"Could not read file: {e}", "warning")
            file_content = f"[Error reading file: {e}]"

    return render_template(
        'explore.html',
        run_id=run_id,
        current_path=str(relative_path),
        breadcrumbs=breadcrumbs,
        is_directory=is_directory,
        items=items,
        file_content=file_content,
        file_download_url=file_download_url # Pass download URL to template
    )

@app.route('/download/<run_id>/<path:sub_path>')
def download_run_file(run_id, sub_path):
    """Provides a specific file from a run directory for download."""
    logging.info(f"Download request for run {run_id}, path: {sub_path}")
    base_run_path = DEMO5_OUTPUT_DIR / f"run_{run_id}"

    # --- Security: Prevent directory traversal (reuse logic or function if desired) --- #
    try:
        if not base_run_path.is_dir():
            logging.error(f"Base run directory not found for download: {base_run_path}")
            abort(404)

        target_path_abs = Path(safe_join(str(base_run_path.resolve()), sub_path)).resolve()

        if not str(target_path_abs).startswith(str(base_run_path.resolve())):
            logging.warning(f"Directory traversal attempt blocked for download: {run_id} / {sub_path}")
            abort(404)

        if not target_path_abs.is_file(): # Ensure it's a file
             logging.warning(f"Attempt to download non-file blocked: {target_path_abs}")
             abort(404)

    except Exception as e:
        logging.error(f"Path safety check error for download {run_id}/{sub_path}: {e}")
        abort(500)
    # --- End Security --- #

    # Use send_from_directory for safer file sending
    try:
        directory = str(target_path_abs.parent)
        filename = target_path_abs.name
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error sending file {target_path_abs}: {e}")
        abort(500)

# --- Streaming Route --- #
@app.route('/stream_task/<run_id>')
def stream_task(run_id):
    """Handles the Server-Sent Events stream for an AI task run."""
    logging.info(f"SSE stream requested for run_id: {run_id}")

    # --- Inner Generator Function --- #
    def generate_stream():
        run_dir = DEMO5_OUTPUT_DIR / f"run_{run_id}"
        task_input = "[Task input not found]"
        model_name = 'llama3'
        ai_bot = None
        full_response_content = ""
        ai_status_summary = "Failed"
        log_filename = "nova_iteration_1_error.md"

        try:
            # --- Setup for this specific stream --- #
            if not run_dir.is_dir():
                yield f"event: error_stream\ndata: Run directory not found for {run_id}\n\n"
                return

            task_file_path = run_dir / "input_task.txt"
            if task_file_path.is_file():
                with open(task_file_path, 'r', encoding='utf-8') as f:
                    task_input = f.read()
            else:
                yield f"event: error_stream\ndata: Task input file not found for {run_id}\n\n"
                return

            # Instantiate Bot for this stream
            bot_base_path = run_dir / "bot_files"
            try:
                ai_bot = BaseBot(base_path=bot_base_path)
                if not ai_bot.ollama_client:
                     raise RuntimeError("Ollama client failed to initialize in BaseBot")
                logging.info(f"[Stream {run_id}] Bot {ai_bot.bot_id} instantiated.")
            except Exception as bot_err:
                 yield f"event: error_stream\ndata: Failed to instantiate AI Bot for stream: {escape(str(bot_err))}\n\n"
                 return

            # --- Prepare Prompt & Log Filename --- #
            prompt = (
                 f"You are simulating the Nova Process. Based on the user's input task/problem below, generate a single iteration report. "
                 f"Follow this exact markdown structure:\n\n"
                 f"Iteration #: 1 (Initial Analysis)\n\n"
                 f"DCE's Instructions:\n[Provide clear instructions based on the user task for hypothetical Agent 1, Agent 2, and the CAE.]\n\n"
                 f"Agent 1 Input (e.g., Software Design Expert):\n[Simulate input from Agent 1, addressing the DCE's instructions based on the user task.]\n\n"
                 f"Agent 2 Input (e.g., Programming Expert):\n[Simulate input from Agent 2, addressing the DCE's instructions based on the user task.]\n\n"
                 f"CAE's Input:\n[Simulate critical analysis from the CAE, evaluating the agents' inputs and highlighting potential risks or improvements related to the user task.]\n\n"
                 f"DCE's Summary:\n[Summarize the key points from the inputs and list specific, actionable goals for the next hypothetical iteration. Pose clarifying questions to the user if necessary.]\n\n"
                 f"---\n"
                 f"USER TASK/PROBLEM:\n{task_input}\n"
                 f"---\n\nGenerate the complete report now based on the user task."
            )
            log_filename = f"nova_iteration_1_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.md"

            # --- Stream the Ollama Response --- #
            stream = ai_bot.ollama_client.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': prompt}],
                stream=True
            )

            for chunk in stream:
                if chunk['done'] == False:
                    content_part = chunk['message']['content']
                    full_response_content += content_part
                    # Escape newlines for SSE data field
                    sse_data = content_part.replace('\n', '\\n')
                    yield f"data: {sse_data}\n\n"
                else:
                    # Stream finished from Ollama's side
                    ai_status_summary = "Success"
                    break # Exit the loop cleanly

            # --- Log Full Response After Stream --- #
            logging.info(f"[Stream {run_id}] Ollama stream finished. Logging full response.")
            log_entry = (
                 f"**Nova Process Simulation (Iteration 1)**\n\n"
                 f"**Model:** `{model_name}`\n"
                 f"**Input Task:**\n```\n{task_input}\n```\n\n"
                 f"**Generated Prompt (for reference):**\n```\n{prompt}\n```\n\n"
                 f"**LLM Raw Output (Simulated Nova Report):**\n---\n{full_response_content}\n---"
            )
            ai_bot.log_action(log_entry, filename=log_filename)

            # --- Generate Summary Report --- #
            summary_content = (
                 f"# Nova Process Simulation Run Summary\n\n"
                 f"**Run ID:** `{run_id}`\n"
                 f"**Status:** {ai_status_summary}\n"
                 f"**Model Used:** `{model_name}`\n\n"
                 f"**Input Task/Problem:**\n```\n{task_input}\n```\n"
            )
            log_file_rel_path = f"bot_files/memory/{log_filename}"
            log_file_url = url_for('explore_run_files', run_id=run_id, sub_path=log_file_rel_path, _external=True) # Use external for clarity if needed
            summary_content += f"\n**View Full Nova Iteration 1 Output:** [{log_filename}]({log_file_url})\n"

            summary_report_path = run_dir / "summary_report.md"
            with open(summary_report_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            logging.info(f"[Stream {run_id}] Generated summary report.")

            # Signal completion to the client
            yield f"event: done\ndata: Stream completed successfully.\n\n"

        except Exception as e:
            error_msg = f"Error during AI stream or processing for run {run_id}: {e}"
            logging.exception(error_msg)
            # Try to log error to bot file if bot was instantiated
            if ai_bot:
                ai_bot.record_event(f"ERROR in stream: {error_msg}")
                # Log error details in the intended log file if possible
                error_log_entry = (
                     f"**Nova Process Simulation FAILED (Iteration 1)**\n\n"
                     f"**Model:** `{model_name}`\n"
                     f"**Input Task:**\n```\n{task_input}\n```\n\n"
                     f"**Generated Prompt:**\n```\n{prompt if 'prompt' in locals() else '[Prompt not generated]'}\n```\n\n"
                     f"**Error:**\n```\n{e}\n```"
                )
                ai_bot.log_action(error_log_entry, filename=log_filename)
            # Signal error to the client
            yield f"event: error_stream\ndata: {escape(error_msg)}\n\n"

    # --- Return the streaming response --- #
    return Response(generate_stream(), mimetype='text/event-stream')

# --- Main Execution ---
if __name__ == '__main__':
    # Ensure the output directory exists before listing runs (edge case on first launch)
    DEMO5_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Run the Flask development server
    # host='0.0.0.0' makes it accessible on the network
    # debug=True enables auto-reloading and Werkzeug debugger (DO NOT USE IN PRODUCTION)
    app.run(host='0.0.0.0', port=5001, debug=True)