import streamlit as st
import pandas as pd
import numpy as np
import itertools
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="BIM-MOO Decision Engine | TRC Project", layout="wide")

# Custom UI Styling for Dark Theme & Academic Precision
st.markdown("""
    <style>
    /* Dark Theme Adjustments */
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; color: #00d4ff !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; color: #ffffff !important; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Box Styling */
    .stMetric { 
        background-color: #161b22; 
        border-radius: 8px; 
        border: 1px solid #30363d;
        border-left: 5px solid #00d4ff;
        padding: 15px;
    }
    
    /* Heading Styling */
    h1, h2, h3 { color: #ffffff; font-family: 'Segoe UI', sans-serif; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    
    /* Sidebar Text Spacing */
    .sidebar-text { line-height: 1.8; font-size: 0.95rem; color: #e6edf3; }
    
    /* Info Box Styling */
    .stAlert { background-color: #161b22; color: #ffffff; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- FULL MATERIAL DICTIONARY ---
descriptions = {
    # CONCRETE CATEGORY
    "OPC Concrete (100% Cement)": "Utilizes 100% Ordinary Portland Cement for high early strength development. It represents the carbon-intensive baseline for institutional structural frames.",
    "Standard M25 Design Mix": "A controlled mix design optimized for standard structural requirements. It balances workability with the mandatory characteristic compressive strength.",
    "PPC Concrete (20% Fly Ash)": "Blended cement concrete that incorporates industrial fly ash to reduce permeability. It enhances long-term durability while lowering the initial hydration heat.",
    "LC3 (Limestone Calcined Clay)": "A low-carbon ternary blend cement that significantly reduces CO2 emissions during clinker production. It offers comparable strength to OPC with superior chloride resistance.",
    "GGBS Concrete (30% Slag)": "Replaces 30% of cement with Ground Granulated Blast-furnace Slag. This selection provides high chemical resistance and is ideal for subsurface institutional foundations.",
    "Green Concrete (40% Fly Ash)": "A sustainable high-volume pozzolanic mix. It substantially lowers the embodied carbon footprint of the structural frame through industrial waste diversion.",
    "Recycled Aggregate Concrete": "Incorporates processed construction and demolition waste as a substitute for natural coarse aggregates. This supports circular economy principles within the TRC project scope.",
    "High Volume GGBS (50%)": "A high-performance eco-blend utilizing 50% slag replacement. It achieves massive carbon reductions but requires extended curing periods for full strength gain.",
    "Geopolymer Concrete": "A zero-cement binder technology activated by alkaline solutions. It represents a breakthrough in carbon-neutral structural engineering for specialized research zones.",
    "Nano-Silica Enhanced Concrete": "Infused with nano-particles to fill micro-pores within the cement matrix. This results in ultra-high density and exceptional service life under aggressive environments.",
    "Carbon-Cured Concrete": "Utilizes mineralization technology to inject and permanently store CO2 within the concrete during the curing process. It turns the structural frame into a functional carbon sink.",
    "Bio-Concrete (Self-Healing)": "Embedded with specialized bacteria that precipitate calcite to seal emerging micro-cracks. This innovation drastically reduces long-term maintenance and life-cycle costs.",

    # MASONRY CATEGORY
    "Traditional Country Bricks": "Local kiln-fired clay units offering high thermal mass and compressive strength. The energy-intensive firing process results in the highest carbon profile in the masonry category.",
    "Wire Cut Bricks": "Machine-pressed units providing superior dimensional accuracy and finish. They reduce mortar consumption but maintain a high embodied energy due to the firing process.",
    "Solid Concrete Blocks": "Precast units manufactured with high compaction for heavy-duty load-bearing walls. They provide a standardized industrial alternative to traditional clay-based masonry.",
    "Hollow Concrete Blocks": "Designed with internal air voids to improve thermal and acoustic insulation. These units reduce the overall dead load on the concrete frame, saving structural costs.",
    "Fly Ash Bricks (Class 7.5)": "Utilizes industrial by-products to create a resource-efficient walling unit. They offer high fire resistance and excellent bonding properties with cement plasters.",
    "Fal-G Bricks": "A blend of Fly Ash, Lime, and Gypsum that hardens through a chemical hydraulic reaction. They eliminate the need for thermal firing, significantly lowering embodied energy.",
    "AAC Blocks (Standard)": "Autoclaved Aerated Concrete units providing superior insulation and high fire ratings. Their lightweight nature allows for faster construction and reduced structural steel requirements.",
    "CLC Blocks (Cellular)": "Foamed concrete blocks containing stable air cells for ultra-lightweight applications. They are highly effective for non-load bearing partitions in laboratory settings.",
    "Porotherm Clay Blocks": "High-tech perforated clay units designed for natural self-insulation. They optimize the thermal comfort of the building envelope without requiring external insulation layers.",
    "Compressed Stabilized Earth": "Manufactured by compacting local soil with minimal cement stabilizer. It offers the lowest possible carbon footprint for walling while providing high aesthetic value.",
    "Sintered Fly Ash Blocks": "Lightweight blocks made from pelletized fly ash. They provide excellent thermal performance and utilize high percentages of industrial waste.",
    "Hempcrete Blocks": "A carbon-negative bio-composite made from hemp shives and lime. It regulates humidity naturally and sequesters more CO2 than is produced during its manufacture.",

    # FLOORING CATEGORY
    "IPS Flooring (Cement Screed)": "A monolithic cement finish providing a hard-wearing industrial surface. It is the most cost-effective solution but lacks advanced aesthetic or acoustic properties.",
    "Ceramic Tiles (Economy)": "Energy-intensive fired clay tiles with a decorative glaze. They offer high hygiene standards for laboratory zones at a competitive procurement cost.",
    "Vitrified Tiles (Standard)": "High-density tiles processed at extreme temperatures to achieve near-zero water absorption. They are ideal for high-traffic institutional corridors and common areas.",
    "Polished Kota Stone": "A natural limestone with high durability and a low carbon footprint due to minimal processing. It is an environmentally robust choice for institutional flooring.",
    "Terrazzo Flooring": "A composite finish consisting of marble or glass chips embedded in a cement binder. It offers a premium, seamless aesthetic with high life-cycle longevity.",
    "Indian Granite": "A high-strength natural stone offering exceptional resistance to chemical spills and abrasion. Its carbon profile is primarily driven by mechanical quarrying and transport.",
    "Industrial Epoxy Coating": "A specialized polymer resin finish providing a seamless, chemical-resistant barrier. Essential for high-precision laboratory environments with strict cleanliness protocols.",
    "Vinyl Flooring (Anti-Static)": "A resilient synthetic finish designed to discharge static electricity. Critical for research zones housing sensitive electronic equipment or server rooms.",
    "Engineered Wood": "Multi-layered timber flooring that provides a warm aesthetic with high dimensional stability. It acts as a carbon storage medium for low-traffic administrative zones.",
    "Bamboo Flooring": "A rapidly renewable flooring solution with strength properties exceeding most hardwoods. It offers a negative carbon sequestration profile for sustainable interiors.",
    "Recycled Rubber Tiles": "Manufactured from salvaged vehicle tires to provide high impact absorption and acoustic damping. Ideal for gymnasiums or heavy-equipment laboratory zones.",
    "Glass-Fused Decorative Tiles": "A premium finish utilizing recycled glass content. While aesthetically superior, the melting process results in a higher embodied energy compared to natural stone."
}

@st.cache_data
def load_and_clean_database():
    try:
        df = pd.read_excel("material_database.xlsx")
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return None

def run_optimization_logic(df, q_c, q_m, q_f):
    concs = df[df['category'].str.contains('concrete', case=False)].to_dict('records')
    masns = df[df['category'].str.contains('masonry', case=False)].to_dict('records')
    flrs = df[df['category'].str.contains('floor', case=False)].to_dict('records')

    all_scenarios = []
    for c, m, f in itertools.product(concs, masns, flrs):
        cost = (c['cost'] * q_c) + (m['cost'] * q_m) + (f['cost'] * q_f)
        ec = (c['ec'] * q_c) + (m['ec'] * q_m) + (f['ec'] * q_f)
        all_scenarios.append({
            "Config": f"{c['material']} + {m['material']} + {f['material']}",
            "Cost": cost, "EC": ec,
            "Concrete": c['material'], "Masonry": m['material'], "Floor": f['material']
        })
    
    res_df = pd.DataFrame(all_scenarios)
    c_min, c_max = res_df['Cost'].min(), res_df['Cost'].max()
    e_min, e_max = res_df['EC'].min(), res_df['EC'].max()
    res_df['C_norm'] = (res_df['Cost'] - c_min) / (c_max - c_min + 1e-9)
    res_df['E_norm'] = (res_df['EC'] - e_min) / (e_max - e_min + 1e-9)
    
    pareto_data = []
    for idx, row in res_df.iterrows():
        if not any((res_df['Cost'] <= row['Cost']) & (res_df['EC'] <= row['EC']) & 
                   ((res_df['Cost'] < row['Cost']) | (res_df['EC'] < row['EC']))):
            pareto_data.append(row)
    return res_df, pd.DataFrame(pareto_data).sort_values("Cost")

# --- APP EXECUTION ---
df = load_and_clean_database()

if df is not None:
    # --- SIDEBAR: REFORMATTED PROJECT SPECS ---
    st.sidebar.title("📄 Project Specifications")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Project Name:**\nTranslational Research Centre (TRC)")
    st.sidebar.markdown("**BIM Quantities :**")
    
    # Each on a new line with symbols
    st.sidebar.markdown(f"🏗️ **Concrete:** 560.77 m³")
    st.sidebar.markdown(f"🧱 **Masonry:** 366.48 m³")
    st.sidebar.markdown(f"📐 **Flooring:** 1550.09 m²")
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Data Source: Phase 1 Revit-Dynamo Extraction")

    # --- MAIN DASHBOARD ---
    st.title("🏛️ Material Optimization Decision System")
    st.markdown("#### BIM-Enabled Multi-Objective Material Optimization for the Translational Research Centre")

    # STEP 1: WEIGHTING WITH NOTATIONS
    st.subheader("I. Calibration of Optimization Weightage")
    col_slide, col_text = st.columns([3, 1.2])
    
    with col_slide:
        wk = st.select_slider("Adjust Environmental Priority ($w_k$):", 
                              options=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], value=0.6)
        wc = round(1.0 - wk, 2)
    
    with col_text:
        st.markdown(f"💰 **Cost Weight ($w_c$):** `{wc}`")
        st.markdown(f"🌿 **Carbon Weight ($w_k$):** `{wk}`")

    full_df, pareto_df = run_optimization_logic(df, 560.77, 366.48, 1550.09)
    full_df['Z'] = (wc * full_df['C_norm']) + (wk * full_df['E_norm'])
    best = full_df.loc[full_df['Z'].idxmin()]

    # STEP 2: OPTIMAL OUTPUTS
    st.markdown("---")
    st.subheader("II. Optimal Solution")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Concrete Spec.", best['Concrete'])
    m2.metric("Masonry Spec.", best['Masonry'])
    m3.metric("Flooring Spec.", best['Floor'])

    # RESULTS SUMMARY
    res_col1, res_col2 = st.columns(2)
    res_col1.info(f"💵 **Estimated Project Cost:** ₹{best['Cost']:,.2f}")
    res_col2.success(f"☁️ **Total Embodied Carbon:** {best['EC']:,.2f} kgCO2e")

    # STEP 3: MATERIAL DESCRIPTIONS
    st.markdown("---")
    st.subheader("III. Technical Performance Insights")
    
    st.info(f"📍 **{best['Concrete']}**: {descriptions.get(best['Concrete'], 'No technical data found.')}")
    st.info(f"📍 **{best['Masonry']}**: {descriptions.get(best['Masonry'], 'No technical data found.')}")
    st.info(f"📍 **{best['Floor']}**: {descriptions.get(best['Floor'], 'No technical data found.')}")

# --- ANALYSIS SECTION ---
    st.markdown("---")
    st.subheader("📊 Pareto Frontier")
    
    fig_p = px.scatter(full_df, x="Cost", y="EC", color="Z", hover_name="Config", 
                       color_continuous_scale="Viridis_r", 
                       template="plotly_dark",
                       labels={"Cost": "Total Cost (₹)", "EC": "Total Carbon (kgCO2e)"})
    
    # Add the Red Pareto Line
    fig_p.add_scatter(x=pareto_df['Cost'], y=pareto_df['EC'], mode='lines+markers', 
                      name='Efficiency Frontier', line=dict(color='red', width=2))
    
    st.plotly_chart(fig_p, use_container_width=True)