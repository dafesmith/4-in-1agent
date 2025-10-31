#!/usr/bin/env python3
"""
Browser Automation MCP Server using Playwright
Enables automated E2E testing of the chatbot frontend
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

mcp = FastMCP("Browser Automation")

# Global browser context
browser_context = None
page = None


class NavigateInput(BaseModel):
    url: str = Field(description="URL to navigate to")
    wait_until: str = Field(
        default="networkidle",
        description="Wait until condition: 'load', 'domcontentloaded', 'networkidle'"
    )


class ClickInput(BaseModel):
    selector: str = Field(description="CSS selector or role-based selector for element to click")
    timeout: int = Field(default=5000, description="Timeout in milliseconds")


class TypeInput(BaseModel):
    selector: str = Field(description="CSS selector for input element")
    text: str = Field(description="Text to type")
    delay: int = Field(default=50, description="Delay between keystrokes in milliseconds")


class WaitForSelectorInput(BaseModel):
    selector: str = Field(description="CSS selector to wait for")
    state: str = Field(
        default="visible",
        description="State to wait for: 'attached', 'detached', 'visible', 'hidden'"
    )
    timeout: int = Field(default=30000, description="Timeout in milliseconds")


class GetTextInput(BaseModel):
    selector: str = Field(description="CSS selector for element")


class ScreenshotInput(BaseModel):
    path: Optional[str] = Field(default=None, description="Path to save screenshot")
    full_page: bool = Field(default=False, description="Capture full scrollable page")


@mcp.tool()
async def start_browser(headless: bool = True) -> str:
    """
    Start a new browser instance with Playwright.

    Args:
        headless: Run browser in headless mode (default True)

    Returns:
        Success message with browser info
    """
    global browser_context, page

    try:
        # Import playwright
        from playwright.async_api import async_playwright

        # Start playwright
        playwright = await async_playwright().start()

        # Launch browser (Chromium by default)
        browser = await playwright.chromium.launch(headless=headless)

        # Create context
        browser_context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        # Create page
        page = await browser_context.new_page()

        return f"✅ Browser started successfully (headless={headless})"

    except Exception as e:
        return f"❌ Failed to start browser: {str(e)}"


@mcp.tool()
async def navigate(url: str, wait_until: str = "networkidle") -> str:
    """
    Navigate to a URL.

    Args:
        url: URL to navigate to
        wait_until: Wait condition ('load', 'domcontentloaded', 'networkidle')

    Returns:
        Success message with page title
    """
    global page

    if page is None:
        return "❌ Browser not started. Call start_browser() first."

    try:
        await page.goto(url, wait_until=wait_until, timeout=30000)
        title = await page.title()
        return f"✅ Navigated to {url} | Page title: {title}"

    except Exception as e:
        return f"❌ Navigation failed: {str(e)}"


@mcp.tool()
async def click_element(selector: str, timeout: int = 5000) -> str:
    """
    Click an element on the page.

    Args:
        selector: CSS selector or text selector
        timeout: Timeout in milliseconds

    Returns:
        Success message
    """
    global page

    if page is None:
        return "❌ Browser not started."

    try:
        await page.click(selector, timeout=timeout)
        return f"✅ Clicked element: {selector}"

    except Exception as e:
        return f"❌ Click failed: {str(e)}"


@mcp.tool()
async def type_text(selector: str, text: str, delay: int = 50) -> str:
    """
    Type text into an input field.

    Args:
        selector: CSS selector for input element
        text: Text to type
        delay: Delay between keystrokes in ms

    Returns:
        Success message
    """
    global page

    if page is None:
        return "❌ Browser not started."

    try:
        await page.fill(selector, "")  # Clear first
        await page.type(selector, text, delay=delay)
        return f"✅ Typed text into {selector}: '{text}'"

    except Exception as e:
        return f"❌ Type failed: {str(e)}"


@mcp.tool()
async def wait_for_selector(
    selector: str,
    state: str = "visible",
    timeout: int = 30000
) -> str:
    """
    Wait for an element to reach a specific state.

    Args:
        selector: CSS selector
        state: State to wait for ('attached', 'detached', 'visible', 'hidden')
        timeout: Timeout in milliseconds

    Returns:
        Success message
    """
    global page

    if page is None:
        return "❌ Browser not started."

    try:
        await page.wait_for_selector(selector, state=state, timeout=timeout)
        return f"✅ Element '{selector}' reached state '{state}'"

    except Exception as e:
        return f"❌ Wait failed: {str(e)}"


@mcp.tool()
async def get_text(selector: str) -> str:
    """
    Get text content of an element.

    Args:
        selector: CSS selector

    Returns:
        Text content of the element
    """
    global page

    if page is None:
        return "❌ Browser not started."

    try:
        text = await page.text_content(selector)
        return f"Text content: {text}"

    except Exception as e:
        return f"❌ Get text failed: {str(e)}"


@mcp.tool()
async def get_all_text(selector: str) -> str:
    """
    Get text content of all matching elements.

    Args:
        selector: CSS selector

    Returns:
        List of text content from all matching elements
    """
    global page

    if page is None:
        return "❌ Browser not started."

    try:
        elements = await page.query_selector_all(selector)
        texts = []
        for elem in elements:
            text = await elem.text_content()
            if text:
                texts.append(text.strip())

        return f"Found {len(texts)} elements:\n" + "\n".join(f"- {t}" for t in texts)

    except Exception as e:
        return f"❌ Get all text failed: {str(e)}"


@mcp.tool()
async def take_screenshot(path: Optional[str] = None, full_page: bool = False) -> str:
    """
    Take a screenshot of the current page.

    Args:
        path: File path to save screenshot (default: /tmp/screenshot.png)
        full_page: Capture full scrollable page

    Returns:
        Success message with screenshot path
    """
    global page

    if page is None:
        return "❌ Browser not started."

    try:
        if path is None:
            path = "/tmp/screenshot.png"

        await page.screenshot(path=path, full_page=full_page)
        return f"✅ Screenshot saved to: {path}"

    except Exception as e:
        return f"❌ Screenshot failed: {str(e)}"


@mcp.tool()
async def get_page_content() -> str:
    """
    Get the full HTML content of the current page.

    Returns:
        HTML content (truncated if too long)
    """
    global page

    if page is None:
        return "❌ Browser not started."

    try:
        content = await page.content()

        # Truncate if too long
        if len(content) > 10000:
            content = content[:10000] + f"\n... (truncated, total length: {len(content)})"

        return content

    except Exception as e:
        return f"❌ Get content failed: {str(e)}"


@mcp.tool()
async def execute_javascript(script: str) -> str:
    """
    Execute JavaScript on the page.

    Args:
        script: JavaScript code to execute

    Returns:
        Result of the JavaScript execution
    """
    global page

    if page is None:
        return "❌ Browser not started."

    try:
        result = await page.evaluate(script)
        return f"JavaScript result: {result}"

    except Exception as e:
        return f"❌ JavaScript execution failed: {str(e)}"


@mcp.tool()
async def check_element_exists(selector: str) -> str:
    """
    Check if an element exists on the page.

    Args:
        selector: CSS selector

    Returns:
        Boolean result indicating if element exists
    """
    global page

    if page is None:
        return "❌ Browser not started."

    try:
        element = await page.query_selector(selector)
        exists = element is not None
        return f"✅ Element '{selector}' exists: {exists}"

    except Exception as e:
        return f"❌ Check failed: {str(e)}"


@mcp.tool()
async def wait_for_load_state(state: str = "networkidle", timeout: int = 30000) -> str:
    """
    Wait for page to reach a specific load state.

    Args:
        state: Load state ('load', 'domcontentloaded', 'networkidle')
        timeout: Timeout in milliseconds

    Returns:
        Success message
    """
    global page

    if page is None:
        return "❌ Browser not started."

    try:
        await page.wait_for_load_state(state, timeout=timeout)
        return f"✅ Page reached load state: {state}"

    except Exception as e:
        return f"❌ Wait for load state failed: {str(e)}"


@mcp.tool()
async def close_browser() -> str:
    """
    Close the browser and clean up resources.

    Returns:
        Success message
    """
    global browser_context, page

    if browser_context is None:
        return "❌ Browser not started."

    try:
        await browser_context.close()
        browser_context = None
        page = None
        return "✅ Browser closed successfully"

    except Exception as e:
        return f"❌ Close browser failed: {str(e)}"


if __name__ == "__main__":
    mcp.run()
