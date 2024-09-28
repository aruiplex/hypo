import time
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

def create_layout():
    """Create a layout with a main area and a fixed summary area at the bottom."""
    layout = Layout()
    layout.split(
        Layout(name="logs", ratio=9),
        Layout(name="summary", size=3)  # Fixed height for summary
    )
    return layout

# Initialize console
console = Console()

# Create layout
layout = create_layout()
layout["logs"].update(Panel(Text("Log messages will appear here...", justify="left"), title="Logs"))
layout["summary"].update(Panel("Summary: Initializing...", title="Summary"))

# Using 'Live' to keep the layout active
with Live(layout, refresh_per_second=10, console=console) as live:
    for i in range(100):
        # Generate a new log entry
        new_log_text = Text(f"Log message {i}", justify="left")
        
        layout["logs"].update(Panel(new_log_text, title="Logs"))
   
        # Update the summary
        layout["summary"].update(Panel(f"Summary: Total logs = {i+1}", title="Summary"))
        
        # Sleep to simulate delay between log entries
        time.sleep(0.5)


