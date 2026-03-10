"""Design tokens and theme constants for the futuristic blue-black UI."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColors:
    """Color palette for the cyber-tech theme."""
    primary_blue: str = "#0D6EFD"
    cyan_accent: str = "#00D4FF"
    neon_blue: str = "#4361EE"
    dark_navy: str = "#0A0E1A"
    darker_bg: str = "#060A14"
    panel_bg: str = "rgba(13, 17, 30, 0.85)"
    card_bg: str = "rgba(16, 22, 40, 0.90)"
    glass_bg: str = "rgba(20, 30, 60, 0.55)"
    border_color: str = "rgba(0, 212, 255, 0.15)"
    glow_color: str = "rgba(0, 212, 255, 0.25)"
    text_primary: str = "#E8EAED"
    text_secondary: str = "#8B95A5"
    text_muted: str = "#5A6577"
    success: str = "#00E676"
    warning: str = "#FFD600"
    error: str = "#FF1744"
    gradient_start: str = "#0A0E1A"
    gradient_mid: str = "#0D1B3E"
    gradient_end: str = "#0A0E1A"


@dataclass(frozen=True)
class ThemeSpacing:
    """Spacing tokens."""
    xs: str = "4px"
    sm: str = "8px"
    md: str = "16px"
    lg: str = "24px"
    xl: str = "32px"
    xxl: str = "48px"


@dataclass(frozen=True)
class ThemeFonts:
    """Font configuration."""
    heading: str = "'Orbitron', 'Rajdhani', 'Segoe UI', sans-serif"
    body: str = "'Inter', 'Segoe UI', -apple-system, sans-serif"
    mono: str = "'JetBrains Mono', 'Fira Code', 'Consolas', monospace"


@dataclass(frozen=True)
class ThemeShadows:
    """Shadow presets."""
    glow_sm: str = "0 0 10px rgba(0, 212, 255, 0.15)"
    glow_md: str = "0 0 20px rgba(0, 212, 255, 0.20)"
    glow_lg: str = "0 0 40px rgba(0, 212, 255, 0.25)"
    card: str = "0 4px 24px rgba(0, 0, 0, 0.4)"
    elevated: str = "0 8px 32px rgba(0, 0, 0, 0.6)"


# ── Singleton instances ───────────────────────────────────────────────
COLORS = ThemeColors()
SPACING = ThemeSpacing()
FONTS = ThemeFonts()
SHADOWS = ThemeShadows()


def get_metric_card_style(accent: str = COLORS.cyan_accent) -> str:
    """Return inline CSS for a glowing metric card."""
    return f"""
        background: {COLORS.card_bg};
        border: 1px solid {COLORS.border_color};
        border-radius: 12px;
        padding: 20px;
        box-shadow: {SHADOWS.glow_sm};
        transition: all 0.3s ease;
    """


def get_panel_style() -> str:
    """Return inline CSS for a glassmorphism panel."""
    return f"""
        background: {COLORS.glass_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid {COLORS.border_color};
        border-radius: 16px;
        padding: 24px;
    """
