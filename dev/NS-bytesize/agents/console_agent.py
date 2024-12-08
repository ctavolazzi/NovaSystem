from typing import Optional, Any, Union, Dict, List
from bots.bot import NovaBot, Agent
from utils.console import NovaConsole, MessageType
from hubs.hub import NovaHub
import json
import asyncio

class ConsoleAgent(NovaBot):
    """
    An agent that provides visual console feedback for all operations.
    Combines NovaBot's AutoGen compatibility with NovaConsole's beautiful output.
    """

    def __init__(self,
                 hub: NovaHub,
                 name: str = "ConsoleAgent",
                 description: Optional[str] = None,
                 show_timestamp: bool = True,
                 debug: bool = False,
                 test_mode: bool = False):
        super().__init__(hub=hub, name=name, description=description)
        self.console = NovaConsole(show_timestamp=show_timestamp, debug=debug)
        self._thinking = False
        self.test_mode = test_mode

    def _format_content(self, content: Union[str, Dict[str, Any]]) -> str:
        """Format message content for display"""
        if isinstance(content, dict):
            return content.get("content", str(content))
        return str(content)

    def _format_message_detail(self, message: Union[Dict[str, Any], str]) -> Optional[Dict[str, Any]]:
        """Format message details for display"""
        if isinstance(message, dict):
            # Remove content from details to avoid duplication
            details = message.copy()
            details.pop("content", None)
            return details if details else None
        return None

    async def _show_thinking(self, action: str):
        """Show a thinking animation"""
        self._thinking = True
        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        try:
            while self._thinking:
                try:
                    if self.test_mode:
                        # In test mode, just print once and exit
                        self.console.print(f"{action}...", MessageType.DEBUG)
                        break
                    self.console.print(f"\r{dots[i]} {action}...", MessageType.DEBUG)
                    await asyncio.sleep(0.1)
                    i = (i + 1) % len(dots)
                    if i > 300:  # 30 seconds (300 * 0.1)
                        self._thinking = False
                        break
                except asyncio.CancelledError:
                    self._thinking = False
                    break
        finally:
            self._thinking = False
            if not self.test_mode:
                print("\r", end="")  # Clear the line

    async def a_send(self,
                    message: Union[Dict[str, Any], str],
                    recipient: "Agent",
                    request_reply: Optional[bool] = None) -> None:
        """Send a message with visual feedback"""
        self.console.info(
            f"Sending message to {recipient.name}",
            detail=self._format_message_detail(message)
        )

        # Show the actual message content
        content = self._format_content(message)
        self.console.print(f"Message: {content}", MessageType.DEBUG)

        await super().a_send(message, recipient, request_reply)
        self.console.success(f"Message sent to {recipient.name}")

    async def a_receive(self,
                       message: Union[Dict[str, Any], str],
                       sender: "Agent",
                       request_reply: Optional[bool] = None) -> None:
        """Receive a message with visual feedback"""
        self.console.info(
            f"Received message from {sender.name}",
            detail=self._format_message_detail(message)
        )

        # Show the actual message content
        content = self._format_content(message)
        self.console.print(f"Message: {content}", MessageType.DEBUG)

        # Start thinking animation if reply is requested
        thinking_task = None
        if request_reply:
            thinking_task = asyncio.create_task(
                self._show_thinking(f"Processing message from {sender.name}")
            )

        try:
            await super().a_receive(message, sender, request_reply)

            if request_reply:
                self.console.debug(f"Reply requested by {sender.name}")
        finally:
            if thinking_task:
                self._thinking = False
                try:
                    await thinking_task
                except asyncio.CancelledError:
                    pass

    async def a_generate_reply(self, messages: List[Dict[str, Any]], sender: Optional[Agent] = None, **kwargs) -> Optional[Union[str, Dict[str, Any]]]:
        """Generate a reply with visual feedback"""
        thinking_task = None
        try:
            # Start thinking animation in the background
            thinking_task = asyncio.create_task(
                self._show_thinking(f"Generating reply to {sender.name if sender else 'message'}")
            )

            # In test mode, wait for the thinking task to complete first
            if self.test_mode and thinking_task:
                await thinking_task

            reply = await super().a_generate_reply(messages, sender, **kwargs)

            if reply:
                self.console.success(
                    "Reply generated",
                    detail=self._format_message_detail(reply)
                )
                content = self._format_content(reply)
                self.console.print(f"Reply: {content}", MessageType.DEBUG)
            else:
                self.console.warning("No reply generated")

            return reply

        except Exception as e:
            self.console.error(f"Error generating reply: {str(e)}")
            raise
        finally:
            # Ensure thinking animation is always stopped
            self._thinking = False
            if thinking_task and not thinking_task.done():
                thinking_task.cancel()
                try:
                    await thinking_task
                except asyncio.CancelledError:
                    pass

    async def cleanup(self):
        """Cleanup with visual feedback"""
        self.console.system("Cleaning up agent resources")
        await super().cleanup()
        self.console.success("Cleanup complete")