#!/usr/bin/env python3
"""
Generate audio files and icons for Ezan Vakti Pro.
Creates:
- assets/icon.svg & assets/icon.png
- assets/pre_warning.wav (Gentle melodic two-tone chime for pre-prayer alert)
- assets/ezan_chime.wav (Harmonic ambient chime for prayer time)
"""

import os
import math
import wave
import struct

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_svg_icon():
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B131E"/>
      <stop offset="50%" stop-color="#111E2E"/>
      <stop offset="100%" stop-color="#060A10"/>
    </linearGradient>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FCD34D"/>
      <stop offset="50%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#D97706"/>
    </linearGradient>
    <linearGradient id="glowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#10B981" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#10B981" stop-opacity="0"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- Background squircle -->
  <rect x="12" y="12" width="232" height="232" rx="54" fill="url(#bgGrad)" filter="url(#shadow)"/>
  <rect x="12" y="12" width="232" height="232" rx="54" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="2"/>

  <!-- Subtle ambient inner glow -->
  <circle cx="128" cy="128" r="90" fill="url(#glowGrad)"/>

  <!-- Crescent Moon and Star -->
  <g transform="translate(128, 120)" filter="url(#shadow)">
    <!-- Crescent -->
    <path d="M 16,-48 A 48,48 0 1 0 16,48 A 38,38 0 1 1 16,-48 Z" 
          fill="url(#goldGrad)" />
    <!-- 8-pointed star -->
    <g transform="translate(26, -6) scale(0.65)">
      <polygon points="0,-16 4,-4 16,0 4,4 0,16 -4,4 -16,0 -4,-4" fill="#FCD34D"/>
      <polygon points="0,-16 4,-4 16,0 4,4 0,16 -4,4 -16,0 -4,-4" fill="#F59E0B" transform="rotate(45)"/>
    </g>
  </g>

  <!-- Mosque Dome and Minaret Silhouette at bottom -->
  <path d="M 64,188 L 64,170 Q 76,170 76,155 L 76,135 Q 76,130 80,126 L 80,188 Z" fill="rgba(255,255,255,0.18)"/>
  <path d="M 192,188 L 192,170 Q 180,170 180,155 L 180,135 Q 180,130 176,126 L 176,188 Z" fill="rgba(255,255,255,0.18)"/>
  <!-- Central Dome -->
  <path d="M 92,188 C 92,145 164,145 164,188 Z" fill="rgba(255,255,255,0.22)"/>
  <!-- Dome Finial -->
  <rect x="126" y="136" width="4" height="12" fill="url(#goldGrad)"/>
  <circle cx="128" cy="134" r="3.5" fill="#FCD34D"/>

  <!-- Baseline border -->
  <line x1="50" y1="188" x2="206" y2="188" stroke="url(#goldGrad)" stroke-width="2" stroke-linecap="round" opacity="0.6"/>
</svg>
"""
    svg_path = os.path.join(ASSETS_DIR, "icon.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated: {svg_path}")

    # Convert to PNG using rsvg-convert or python cairo if available
    png_path = os.path.join(ASSETS_DIR, "icon.png")
    os.system(f"rsvg-convert -w 256 -h 256 '{svg_path}' -o '{png_path}' 2>/dev/null || true")
    if not os.path.exists(png_path) or os.path.getsize(png_path) == 0:
        # Fallback to python-cairo conversion
        try:
            import gi
            gi.require_version('Rsvg', '2.0')
            from gi.repository import Rsvg, cairo
            handle = Rsvg.Handle.new_from_file(svg_path)
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 256, 256)
            cr = cairo.Context(surf)
            handle.render_cairo(cr)
            surf.write_to_png(png_path)
            print(f"Generated PNG via Rsvg: {png_path}")
        except Exception as e:
            print(f"PNG generation fallback notice: {e}")

def generate_wav(filepath, duration_sec, freq_list, sample_rate=44100):
    """
    Synthesize rich harmonic chimes with smooth attack and decay.
    """
    total_samples = int(duration_sec * sample_rate)
    samples = []

    for i in range(total_samples):
        t = float(i) / sample_rate
        val = 0.0

        for note_start, note_dur, base_freq in freq_list:
            if note_start <= t < (note_start + note_dur):
                dt = t - note_start
                # Attack - Decay envelope
                attack = min(1.0, dt / 0.02)
                decay = math.exp(-3.5 * dt / note_dur)
                env = attack * decay

                # Harmonics
                h1 = math.sin(2.0 * math.pi * base_freq * dt)
                h2 = 0.45 * math.sin(2.0 * math.pi * (base_freq * 2) * dt)
                h3 = 0.20 * math.sin(2.0 * math.pi * (base_freq * 3) * dt)
                h4 = 0.10 * math.sin(2.0 * math.pi * (base_freq * 4.2) * dt)

                val += (h1 + h2 + h3 + h4) * env * 0.35

        # Clamp
        val = max(-1.0, min(1.0, val))
        samples.append(int(val * 32767.0))

    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        data = struct.pack(f"<{len(samples)}h", *samples)
        wf.writeframes(data)
    print(f"Generated Audio: {filepath}")

def main():
    generate_svg_icon()

    # 1. Pre-prayer warning chime (Gentle uplifting 2-tone melodic notification)
    # E5 (659Hz) -> B5 (987Hz)
    pre_tones = [
        (0.00, 0.65, 659.25),
        (0.25, 1.20, 987.77)
    ]
    generate_wav(os.path.join(ASSETS_DIR, "pre_warning.wav"), 1.6, pre_tones)

    # 2. Prayer time ambient chime (Solemn 3-chord harmonic tone)
    # C5 (523Hz) -> G5 (783Hz) -> C6 (1046Hz)
    prayer_tones = [
        (0.00, 1.2, 523.25),
        (0.20, 1.4, 659.25),
        (0.40, 2.0, 783.99),
        (0.70, 2.4, 1046.50)
    ]
    generate_wav(os.path.join(ASSETS_DIR, "ezan_chime.wav"), 3.2, prayer_tones)

if __name__ == "__main__":
    main()
