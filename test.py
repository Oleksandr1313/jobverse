import streamlit as st
import colorsys
import matplotlib.pyplot as plt

st.set_page_config(page_title="Color Palette Explorer", page_icon="🎨")

st.title("🎨 Color Palette Explorer")
st.write("Choose a base color and palette type to explore color combinations!")

# Color input
base_color = st.color_picker("Pick a base color", "#3498db")

# Palette type
palette_type = st.selectbox("Palette type", ["Complementary", "Analogous", "Triadic"])

# Convert hex to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

# Generate palette
def generate_palette(base_hex, mode):
    r, g, b = hex_to_rgb(base_hex)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    palette = []

    if mode == "Complementary":
        h2 = (h + 0.5) % 1.0
        palette = [colorsys.hls_to_rgb(h, l, s), colorsys.hls_to_rgb(h2, l, s)]
    elif mode == "Analogous":
        palette = [colorsys.hls_to_rgb((h + shift) % 1.0, l, s) for shift in (-0.1, 0, 0.1)]
    elif mode == "Triadic":
        palette = [colorsys.hls_to_rgb((h + shift) % 1.0, l, s) for shift in (0, 1/3, 2/3)]

    return ["#" + "".join(f"{int(c*255):02x}" for c in rgb) for rgb in palette]

# Display palette
palette = generate_palette(base_color, palette_type)
st.subheader("Generated Palette:")
for color in palette:
    st.markdown(f"<div style='background-color:{color};padding:10px;color:white'>{color}</div>", unsafe_allow_html=True)