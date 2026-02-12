import os, json
from flask import render_template_string
from src. models import LogEntry
def list_logs():
    """
    Scans the logs directory and renders an HTML dashboard listing all historical builds.
    
    Returns:
        str: An HTML table displaying build commits and links to detailed reports.
    """
    os.makedirs("logs", exist_ok=True)
    
    log_files = sorted(os.listdir("logs"), reverse=True)

    html = """
    <html>
    <head><title>CI Build History</title></head>
    <body style="font-family: sans-serif; margin: 40px;">
        <h1> Build History</h1>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            <tr style="background: #eee;">
                <th>Commit</th>
                
                <th>Link</th>
            </tr>
            {% for log in logs %}
            <tr>
                <td>{{ log.split('_')[0] }}</td>
                
                <td><a href="/logs/{{ log }}">Link</a></td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """

    return render_template_string(html, logs=log_files)



def view_log(filename):
    """
    Retrieves and displays the details of a specific build log.
    
    Args:
        filename (str): The name of the log file to read.
        
    Returns:
        str: A formatted HTML page showing build metadata and console output.
    """
    path = os.path.join("logs", filename)
    if not os.path.exists(path): return "Not Found", 404

    with open(path, "r") as f:
        raw_content = f.read()

    try:

        data = json.loads(raw_content)
        meta = f"SHA: {data.get('commit_SHA')}"
        logs = data.get('gradle_output', "No logs found.")
    except:
        meta, logs = "Raw Log File", raw_content

    return render_template_string("""
        <body style="font-family:monospace; padding:20px;">
            <h3>📄 {{ meta }}</h3>
            <pre style="padding:15px; border-radius:5px; overflow-x:auto;">{{ logs }}</pre>
            <a href="/logs">← Back</a>
        </body>
    """, meta=meta, logs=logs)


def save_log_to_file(entry: LogEntry):
    """
    Persists a BuildReport to the local filesystem as a unique log file.
    
    Args:
        entry (LogEntry): The object containing commit info, status, and build logs.
    """
    """Helper to save the LogEntry string to a file."""
    filename = entry.generate_log_file_name()
    with open(f"logs/{filename}", "w") as f:
        f.write(str(entry))
