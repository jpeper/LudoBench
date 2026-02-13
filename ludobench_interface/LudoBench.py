import gradio as gr
import pandas as pd



# Intro text (Markdown)
intro_text = """
# LudoBench: Evaluating Multimodal Reasoning through Real-World Tabletop Strategy Games

📑 [Paper](#) | 💻 [GitHub](#) | 🤗 [Public Dataset](#) | ⚙️ Version: V1 | # Models: 7 | Updated: September 2025
"""


# --- Data for each Tier ---
tier1_rows = [
    {"Model":"GPT-4o",         "KingD None":0.38, "KingD Text":0.57, "KingD Image":0.43,
                               "ResArc None":0.65, "ResArc Text":0.65, "ResArc Image":0.57,
                               "PaxRen None":0.38, "PaxRen Text":0.47, "PaxRen Image":0.60},
    {"Model":"o1",             "KingD None":0.52, "KingD Text":0.43, "KingD Image":0.43,
                               "ResArc None":0.68, "ResArc Text":0.53, "ResArc Image":0.60,
                               "PaxRen None":0.45, "PaxRen Text":0.55, "PaxRen Image":0.47},
    {"Model":"GPT-4.1",        "KingD None":0.62, "KingD Text":0.52, "KingD Image":0.62,
                               "ResArc None":0.78, "ResArc Text":0.72, "ResArc Image":0.75,
                               "PaxRen None":0.53, "PaxRen Text":0.57, "PaxRen Image":0.60},
    {"Model":"Gemini Flash 2.5","KingD None":0.52, "KingD Text":0.48, "KingD Image":0.38,
                               "ResArc None":0.68, "ResArc Text":0.78, "ResArc Image":0.50,
                               "PaxRen None":0.55, "PaxRen Text":0.40, "PaxRen Image":0.38},
    {"Model":"Gemini Pro 2.5", "KingD None":0.52, "KingD Text":0.52, "KingD Image":0.33,
                               "ResArc None":0.65, "ResArc Text":0.70, "ResArc Image":0.53,
                               "PaxRen None":0.65, "PaxRen Text":0.72, "PaxRen Image":0.38},
    {"Model":"Qwen2.5VL-32B",  "KingD None":0.30, "KingD Text":0.47, "KingD Image":0.40,
                               "ResArc None":0.47, "ResArc Text":0.50, "ResArc Image":0.40,
                               "PaxRen None":0.47, "PaxRen Text":0.47, "PaxRen Image":0.38},
    {"Model":"Claude 3.7 Sonnet","KingD None":0.42,"KingD Text":0.65, "KingD Image":0.60,
                               "ResArc None":0.70, "ResArc Text":0.78, "ResArc Image":0.60,
                               "PaxRen None":0.42, "PaxRen Text":0.53, "PaxRen Image":0.38},
]

tier2_rows = [
    {"Model":"GPT-4o",         "KingD None":0.30, "KingD Text":0.43, "KingD Image":0.30,
                               "ResArc None":0.27, "ResArc Text":0.40, "ResArc Image":0.37,
                               "PaxRen None":0.13, "PaxRen Text":0.53, "PaxRen Image":0.50},
    {"Model":"o1",             "KingD None":0.20, "KingD Text":0.40, "KingD Image":0.27,
                               "ResArc None":0.40, "ResArc Text":0.40, "ResArc Image":0.37,
                               "PaxRen None":0.20, "PaxRen Text":0.43, "PaxRen Image":0.43},
    {"Model":"GPT-4.1",        "KingD None":0.33, "KingD Text":0.43, "KingD Image":0.30,
                               "ResArc None":0.50, "ResArc Text":0.53, "ResArc Image":0.47,
                               "PaxRen None":0.30, "PaxRen Text":0.47, "PaxRen Image":0.40},
    {"Model":"Gemini Flash 2.5","KingD None":0.17, "KingD Text":0.30, "KingD Image":0.27,
                               "ResArc None":0.20, "ResArc Text":0.37, "ResArc Image":0.40,
                               "PaxRen None":0.20, "PaxRen Text":0.27, "PaxRen Image":0.33},
    {"Model":"Gemini Pro 2.5", "KingD None":0.37, "KingD Text":0.37, "KingD Image":0.27,
                               "ResArc None":0.47, "ResArc Text":0.53, "ResArc Image":0.47,
                               "PaxRen None":0.10, "PaxRen Text":0.43, "PaxRen Image":0.23},
    {"Model":"Qwen2.5VL-32B",  "KingD None":0.43, "KingD Text":0.20, "KingD Image":0.30,
                               "ResArc None":0.40, "ResArc Text":0.33, "ResArc Image":0.50,
                               "PaxRen None":0.10, "PaxRen Text":0.10, "PaxRen Image":0.50},
    {"Model":"Claude 3.7 Sonnet","KingD None":0.13,"KingD Text":0.27, "KingD Image":0.23,
                               "ResArc None":0.47, "ResArc Text":0.50, "ResArc Image":0.57,
                               "PaxRen None":0.07, "PaxRen Text":0.37, "PaxRen Image":0.40},
]

tier3_rows = [
    {"Model":"GPT-4o",         "KingD None":0.00, "KingD Text":0.00, "KingD Image":0.00,
                               "ResArc None":0.03, "ResArc Text":0.12, "ResArc Image":0.05,
                               "PaxRen None":0.06, "PaxRen Text":0.12, "PaxRen Image":0.07},
    {"Model":"o1",             "KingD None":0.00, "KingD Text":0.02, "KingD Image":0.00,
                               "ResArc None":0.07, "ResArc Text":0.08, "ResArc Image":0.07,
                               "PaxRen None":0.15, "PaxRen Text":0.06, "PaxRen Image":0.12},
    {"Model":"GPT-4.1",        "KingD None":0.00, "KingD Text":0.02, "KingD Image":0.10,
                               "ResArc None":0.05, "ResArc Text":0.08, "ResArc Image":0.07,
                               "PaxRen None":0.07, "PaxRen Text":0.10, "PaxRen Image":0.07},
    {"Model":"Gemini Flash 2.5","KingD None":0.04, "KingD Text":0.08, "KingD Image":0.10,
                               "ResArc None":0.05, "ResArc Text":0.08, "ResArc Image":0.07,
                               "PaxRen None":0.13, "PaxRen Text":0.13, "PaxRen Image":0.12},
    {"Model":"Gemini Pro 2.5", "KingD None":0.00, "KingD Text":0.02, "KingD Image":0.00,
                               "ResArc None":0.12, "ResArc Text":0.30, "ResArc Image":0.08,
                               "PaxRen None":0.07, "PaxRen Text":0.09, "PaxRen Image":0.07},
    {"Model":"Qwen2.5VL-32B",  "KingD None":0.04, "KingD Text":0.05, "KingD Image":0.05,
                               "ResArc None":0.02, "ResArc Text":0.05, "ResArc Image":0.07,
                               "PaxRen None":0.04, "PaxRen Text":0.09, "PaxRen Image":0.12},
    {"Model":"Claude 3.7 Sonnet","KingD None":0.22,"KingD Text":0.12, "KingD Image":0.07,
                               "ResArc None":0.07, "ResArc Text":0.08, "ResArc Image":0.10,
                               "PaxRen None":0.07, "PaxRen Text":0.10, "PaxRen Image":0.12},
]

# --- Summarize best modality per game + tier ---
def summarize_game(t1, t2, t3, game_prefix, game_name):
    rows = []
    for i, model in enumerate([r["Model"] for r in t1]):  # assumes same model order
        t1_best = max(t1[i][f"{game_prefix} None"],
                      t1[i][f"{game_prefix} Text"],
                      t1[i][f"{game_prefix} Image"])
        t2_best = max(t2[i][f"{game_prefix} None"],
                      t2[i][f"{game_prefix} Text"],
                      t2[i][f"{game_prefix} Image"])
        t3_best = max(t3[i][f"{game_prefix} None"],
                      t3[i][f"{game_prefix} Text"],
                      t3[i][f"{game_prefix} Image"])
        overall = (t1_best + t2_best + t3_best) / 3
        rows.append({
            "Model": model,
            "Tier 1": round(t1_best, 2),
            "Tier 2": round(t2_best, 2),
            "Tier 3": round(t3_best, 2),
            "Overall": round(overall, 2)
        })
    return pd.DataFrame(rows)

# Build tables per game
df_king = summarize_game(tier1_rows, tier2_rows, tier3_rows, "KingD", "Kingdomino")
df_resarc = summarize_game(tier1_rows, tier2_rows, tier3_rows, "ResArc", "Res Arcana")
df_pax = summarize_game(tier1_rows, tier2_rows, tier3_rows, "PaxRen", "Pax Renaissance")

# --- Leaderboard tab content ---
def leaderboard_tab():
    with gr.Blocks() as demo:
        gr.Markdown("## 🏆 LudoBench Leaderboard")
        gr.Markdown(
            """
            The leaderboard reports accuracy of different multimodal models across **three tiers of reasoning**, 
            evaluated on three diverse tabletop strategy games (*Kingdomino, Res Arcana,* and *Pax Renaissance 2e*):  
            
            - **Tier 1: Environment Perception** – recognizing objects and counts.  
            - **Tier 2: Rules Integration** – applying multimodal rulebook knowledge.  
            - **Tier 3: Short-Horizon Optimization** – planning optimal short-term moves.  
            
            Models are evaluated under three **rulebook modalities**:  
            - **None** (parametric knowledge only)  
            - **Text** (text-only rulebook)  
            - **Image** (image-based rulebook)  
            """
        )

        gr.Markdown("### Choose a game to view model performance")

        game_selector = gr.Dropdown(
            choices=["Kingdomino", "Res Arcana", "Pax Renaissance"],
            value="Kingdomino",
            label="Select Game"
        )

        # Initial table (Kingdomino)
        table = gr.Dataframe(
            value=df_king,
            interactive=False,
            label="Leaderboard Results",
            wrap=True
        )

        # Callback
        def get_table(choice):
            if choice == "Kingdomino":
                return df_king
            elif choice == "Res Arcana":
                return df_resarc
            else:
                return df_pax

        game_selector.change(fn=get_table, inputs=game_selector, outputs=table)

        # Styling
        gr.HTML(
            """
            <style>
                [data-testid="dataframe"] table th:nth-child(1),
                [data-testid="dataframe"] table td:nth-child(1) {
                    font-weight: bold;
                    background: #222;
                    color: #fff;
                    min-width: 200px;
                }
            </style>
            """
        )


# # Leaderboard tab content
# def leaderboard_tab():
#     with gr.Blocks() as demo:
#         gr.Markdown("## 🏆 LudoBench Leaderboard")
#         gr.Markdown(
#             """
#             The leaderboard reports accuracy of different multimodal models across **three tiers of reasoning**, 
#             evaluated on three diverse tabletop strategy games (*Kingdomino, Res Arcana,* and *Pax Renaissance 2e*):  
            
#             - **Tier 1: Environment Perception** – recognizing objects and counts.  
#             - **Tier 2: Rules Integration** – applying multimodal rulebook knowledge.  
#             - **Tier 3: Short-Horizon Optimization** – planning optimal short-term moves.  
            
#             Models are evaluated under three **rulebook modalities**:  
#             - **None** (parametric knowledge only)  
#             - **Text** (text-only rulebook)  
#             - **Image** (image-based rulebook)  
#             """
#         )

#         gr.Markdown("### Choose a tier to view model accuracies across games & modalities")

#         tier_selector = gr.Dropdown(
#             choices=[
#                 "All Tiers",
#                 "Tier 1: Perception",
#                 "Tier 2: Rules Integration",
#                 "Tier 3: Short-horizon Optimization",
#             ],
#             value="All Tiers",
#             label="Select Tier"
#         )

#         # Initial table (all tiers, collapsed labels)
#         table = gr.Dataframe(
#             value=collapse_tier_labels(df_all),
#             interactive=False,
#             label="Leaderboard Results",
#             wrap=True
#         )

#         # Callback
#         def get_table(choice):
#             if choice == "Tier 1: Perception":
#                 return df_t1.drop(columns=["Tier"])
#             elif choice == "Tier 2: Rules Integration":
#                 return df_t2.drop(columns=["Tier"])
#             elif choice == "Tier 3: Short-horizon Optimization":
#                 return df_t3.drop(columns=["Tier"])
#             else:
#                 return collapse_tier_labels(df_all)

#         tier_selector.change(fn=get_table, inputs=tier_selector, outputs=table)

#         # Styling
#         gr.HTML(
#             """
#             <style>
#                 [data-testid="dataframe"] table th:nth-child(1),
#                 [data-testid="dataframe"] table td:nth-child(1) {
#                     font-weight: bold;
#                     background: #222;
#                     color: #fff;
#                     min-width: 200px;
#                 }
#             </style>
#             """
#         )


# Benchmark Tab content
def benchmark_tab():
    
    # --- Abstract Section ---
    gr.Markdown("## Abstract")
    gr.Markdown("""
        LudoBench is a multimodal game reasoning benchmark designed to evaluate how well vision-enabled language 
        models handle real-world tabletop strategy games. Unlike prior benchmarks that focus mainly on familiar 
        board games, LudoBench recreates the experience of players learning and applying new rules for the first time.

        LudoBench includes 400 annotated question–answer examples drawn from three diverse games: *Kingdomino, Res Arcana,* 
        and *Pax Renaissance (2nd Edition)*. These games are chosen based on increasing complexity of game states and rules comprehension.
        Average accuracy reaches only **∼53%** on Tier 1 perception tasks, drops to **∼34%** on Tier 2 rule integration, and falls further to 
        just **∼7–10%** on Tier 3 short-horizon optimization.  
        
        These results highlight the steep decline in accuracy as task complexity increases, underscoring current limitations of 
        multimodal reasoning in complex, rules-driven domains.
    """)

    
    # --- Pipeline / Methodology Section ---
    # with gr.Tab("Benchmark"):
    gr.Markdown("## Pipeline / Methodology")

    gr.Image(
        value="/Users/shlokijha/Desktop/Ludobench Interface/pipeline-1.png",
        label="LudoBench Pipeline",
        show_label=True,
        elem_id="pipeline-diagram"
    )


# --- Gradio Interface ---
with gr.Blocks() as demo:
    # Add intro
    gr.Markdown(intro_text)
    
    # Tabs
    with gr.Tabs():
        with gr.TabItem("Leaderboard"):
            gr.Markdown(leaderboard_tab())
        with gr.TabItem("Benchmark"):
            gr.Markdown(benchmark_tab())

demo.launch()
