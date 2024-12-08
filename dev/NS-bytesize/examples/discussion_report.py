import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from hubs.discussion_hub import DiscussionHub
from utils.console import NovaConsole, ConsoleColor, MessageType
from utils.task_handler import TaskHandler

class ConsoleHUD:
    def __init__(self):
        self.console = NovaConsole(show_timestamp=True)
        self._last_status = ""
        self._progress = 0
        self._current_agent = ""
        self._last_message = ""
        self._messages = []  # Store recent messages
        self._max_messages = 5  # Number of messages to show

    def update_status(self, status: str):
        """Update the main status message."""
        self._last_status = status
        self._render()

    def update_progress(self, progress: int, message: str):
        """Update the progress bar."""
        self._progress = progress
        self._last_status = message
        self._render()

    def update_agent(self, agent: str, message: str):
        """Update the current speaking agent and their message."""
        self._current_agent = agent
        self._last_message = message
        self._messages.append((agent, message))
        if len(self._messages) > self._max_messages:
            self._messages.pop(0)
        self._render()

    def _render(self):
        """Render the HUD to the console."""
        self.console.clear()  # Clear previous output

        # Title
        self.console.system("╔══════════════════════════════════════════════════════════════╗")
        self.console.system("║              Discussion Report Generator - Live HUD          ║")
        self.console.system("╚══════════════════════════════════════════════════════════════╝")

        # Status and Progress
        self.console.info(f"Current Status: {self._last_status}")
        self.console.progress(
            current=self._progress,
            total=100,
            prefix="Overall Progress",
            suffix=f"{self._progress}%",
            bar_length=40
        )

        # Recent Messages
        self.console.system("\nRecent Agent Activity:")
        self.console.system("────────────────────────────────────────────────────────────")
        for agent, msg in self._messages[-self._max_messages:]:
            truncated_msg = msg[:100] + "..." if len(msg) > 100 else msg
            print(f"\n{ConsoleColor.CYAN}{agent}{ConsoleColor.END}:")
            # Split message into lines for better readability
            for line in truncated_msg.split('\n'):
                print(f"{ConsoleColor.YELLOW}  {line.strip()}{ConsoleColor.END}")

        # Footer
        self.console.system("\n════════════════════════════════════════════════════════════")

class DiscussionReporter:
    def __init__(self):
        self.hub = DiscussionHub()
        self.hud = ConsoleHUD()
        self.task_handler = TaskHandler("discussion_report")
        self.reports_dir = Path("discussion_reports")
        self.reports_dir.mkdir(exist_ok=True)

    async def generate_report(self, topic: str) -> str:
        """Generate a discussion report on the given topic."""
        self.hud.update_status("Initializing discussion...")

        try:
            # Initialize discussion
            self.hud.update_progress(10, "Setting up discussion environment...")
            await asyncio.sleep(0.5)  # Allow HUD to update

            # Start discussion
            self.hud.update_progress(20, "Starting discussion with AI agents...")
            discussion_id = await self.hub.start_discussion(topic)
            self.hud.update_agent("Discussion Controller", "Analyzing topic and creating discussion plan...")
            await asyncio.sleep(0.5)  # Allow HUD to update

            # Add follow-up questions for deeper analysis
            follow_ups = [
                "What are the key challenges or potential issues we should consider?",
                "What are the most promising opportunities or solutions?",
                "What specific actions or next steps would you recommend?",
                "Are there any important dependencies or prerequisites to consider?"
            ]

            for i, question in enumerate(follow_ups, 1):
                progress = 30 + (i * 10)
                self.hud.update_progress(progress, f"Processing follow-up question {i}/{len(follow_ups)}...")
                self.hud.update_agent("Discussion Coordinator", question)
                await self.hub.add_message_to_discussion(discussion_id, question)
                await asyncio.sleep(0.5)  # Allow HUD to update

            # Generate insights
            self.hud.update_progress(70, "Analyzing discussion points...")
            self.hud.update_agent("Analysis Engine", "Extracting key insights and recommendations...")
            await asyncio.sleep(0.5)  # Allow HUD to update

            # Get final summary
            self.hud.update_progress(80, "Generating final summary...")
            self.hud.update_agent("Discussion Controller", "Preparing comprehensive discussion summary...")
            summary = await self.hub.end_discussion(discussion_id)

            # Create report
            self.hud.update_progress(90, "Creating report document...")
            self.hud.update_agent("Report Generator", "Formatting discussion results and recommendations...")
            report = self._format_report(topic, summary)

            # Save report
            self.hud.update_progress(95, "Saving report...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.reports_dir / f"discussion_report_{timestamp}.md"
            report_path.write_text(report)

            self.hud.update_progress(100, "Report completed!")
            self.hud.update_agent("System", f"Report saved successfully to: {report_path}")
            await asyncio.sleep(1)  # Show completion message

            return report

        except Exception as e:
            self.hud.update_status(f"Error: {str(e)}")
            self.hud.update_agent("System", "An error occurred during report generation")
            raise

    def _format_report(self, topic: str, summary: str) -> str:
        """Format the discussion results into a markdown report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""# Discussion Report: {topic}

## Overview
Generated on: {timestamp}

## Topic
{topic}

## Discussion Summary
{summary}

## Analysis and Recommendations
{self._extract_sections(summary)}

## Next Steps
{self._extract_next_steps(summary)}
"""

    def _extract_sections(self, summary: str) -> str:
        """Extract and format key sections from the summary."""
        # The AI agents' summaries are usually well-structured
        # We'll return them as-is for now, but could add more processing
        return summary

    def _extract_next_steps(self, summary: str) -> str:
        """Extract action items and next steps from the summary."""
        # For now, return the relevant part of the summary
        # Could add more sophisticated extraction later
        return summary

async def main():
    parser = argparse.ArgumentParser(description="Generate an AI-powered discussion report on any topic.")
    parser.add_argument("topic", help="The topic or question to discuss")
    args = parser.parse_args()

    reporter = DiscussionReporter()
    await reporter.generate_report(args.topic)

if __name__ == "__main__":
    asyncio.run(main())