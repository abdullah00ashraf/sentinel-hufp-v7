import matplotlib.pyplot as plt

# --- 1. DATA SETUP (1,000 Trapped Epistemic Hallucinations) ---
labels = [
    'CAPILLARY FRINGE SATURATION PARADOX',
    'TOPOGRAPHIC ELEVATION VIOLATION',
    'SAR-VH VS OPTICAL CONFLICT',
    'DEMOGRAPHIC VULNERABILITY TRIGGER',
    'MASS BALANCE ASYMMETRY'
]

# The percentage breakdown of which rules caught the errors
sizes = [21.8, 21.1, 20.1, 19.1, 17.9]

# --- 2. TACTICAL THEME COLORS ---
# Highlight the most common trap in Tactical Yellow, fade the rest into deep greys
colors = ['#EAB308', '#A3A3A3', '#737373', '#525252', '#333333']

# Create the canvas
fig, ax = plt.subplots(figsize=(11, 6), facecolor='#171717')

# --- 3. RENDER THE DONUT CHART ---
# wedgeprops creates the "Donut" effect by setting a width, and adds a sleek dark border between slices
wedges, texts, autotexts = ax.pie(
    sizes, 
    colors=colors, 
    autopct='%1.1f%%',
    startangle=160,
    pctdistance=0.82,
    wedgeprops=dict(width=0.35, edgecolor='#171717', linewidth=3)
)

# Style the percentage text inside the slices
for i, autotext in enumerate(autotexts):
    # Dark text for the yellow slice, white text for the dark grey slices
    autotext.set_color('#171717' if i == 0 else '#FFFFFF')
    autotext.set_fontweight('bold')
    autotext.set_family('monospace')
    autotext.set_fontsize(10)

# --- 4. THE COMMAND CENTER HUD (Center Text) ---
# Add the massive "1,000" in the center hole of the donut
ax.text(0, 0.12, '1,000', ha='center', va='center', fontsize=42, fontweight='bold', color='#FFFFFF', family='monospace')
ax.text(0, -0.15, 'EPISTEMIC THREATS\nPURGED', ha='center', va='center', fontsize=11, color='#A3A3A3', family='monospace')

# --- 5. TACTICAL LEGEND ---
legend = ax.legend(wedges, labels, 
                   title="PARADOX TRAP CLASSIFICATION", 
                   loc="center left", 
                   bbox_to_anchor=(1.05, 0.5), 
                   frameon=False)

# Style the legend text and title
plt.setp(legend.get_texts(), color='#D4D4D4', family='monospace', fontsize=10)
plt.setp(legend.get_title(), color='#EAB308', family='monospace', fontweight='bold', fontsize=11)

# Add Title and Metadata
plt.title('PHYSICAL GUARDRAILS: OUT-OF-DISTRIBUTION CHAOS', color='#EAB308', pad=20, fontweight='bold', fontsize=14, loc='left')
plt.figtext(0.13, 0.05, "DATA SOURCE: MONTE CARLO DROPOUT INFERENCE | BASELINE: GAUSSIAN NOISE INJECTION", 
            color='#737373', fontsize=9, family='monospace')

# --- 6. EXPORT HIGH-RES IMAGE ---
plt.tight_layout()
plt.savefig('TACTICAL_DONUT_CHART.png', dpi=400, bbox_inches='tight', facecolor='#171717')
print("✅ SUCCESS: High-Resolution Tactical Donut saved as 'TACTICAL_DONUT_CHART.png'")