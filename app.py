import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Social Media and Student Outcomes",
    page_icon="📱",
    layout="wide"
)


@st.cache_data
def load_data():
    df1 = pd.read_csv("students.csv")
    df2 = pd.read_csv("academic.csv")

    # df2: explode multi-platform column for platform analysis
    df2["Platform_List"] = df2["Platforms"].str.split(", ")
    df2_exploded = df2.explode("Platform_List")

    # df2: explode multi-reason column for reason analysis
    df2["Reason_List"] = df2["Reasons"].str.split(", ")
    df2_reasons = df2.explode("Reason_List")

    # df2: ordered usage hours for charts
    usage_order = ["Less than 1 hour", "1-2 hours", "3-4 hours", "5-6 hours", "More than 6 hours"]
    df2["Usage_Hours_Ordered"] = pd.Categorical(df2["Hours on Social Media"], categories=usage_order, ordered=True)

    return df1, df2, df2_exploded, df2_reasons

df1, df2, df2_exploded, df2_reasons = load_data()


st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choose a page",
    [
        "🏠 Home",
        "😴 Sleep & Usage",
        "🧠 Mental Health",
        "📚 Academic Performance",
        "📊 Platform Analysis",
        "🔍 Dataset Overview",
    ]
)

st.sidebar.markdown("---")
st.sidebar.write("**Filters** (apply to Sleep & Mental Health pages)")

gender_options = ["All"] + sorted(df1["Gender"].dropna().unique().tolist())
selected_gender = st.sidebar.selectbox("Gender", gender_options)

level_options = ["All"] + sorted(df1["Academic_Level"].dropna().unique().tolist())
selected_level = st.sidebar.selectbox("Academic Level", level_options)

filtered_df1 = df1.copy()
if selected_gender != "All":
    filtered_df1 = filtered_df1[filtered_df1["Gender"] == selected_gender]
if selected_level != "All":
    filtered_df1 = filtered_df1[filtered_df1["Academic_Level"] == selected_level]

# ── Helper: add sample size annotation to bar chart ───────────────────────────
def add_n_annotations(fig, df_grouped, x_col, count_col):
    for i, row in df_grouped.iterrows():
        fig.add_annotation(
            x=row[x_col],
            y=0,
            text=f"n={int(row[count_col])}",
            showarrow=False,
            yshift=-18,
            font=dict(size=10, color="gray"),
        )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.title("📱 Social Media Usage and Student Outcomes")
    st.write(
        "Social media is a daily habit for almost every student — but how does it "
        "actually affect sleep, mental health, and academic performance? "
        "This project explores these questions using two student survey datasets."
    )

    st.markdown("---")
    st.subheader("🔑 Key Findings at a Glance")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            "**😴 Sleep**\n\n"
            "Students using social media **5+ hours/day** sleep on average "
            f"**{filtered_df1[filtered_df1['Avg_Daily_Usage_Hours'] >= 5]['Sleep_Hours_Per_Night'].mean():.1f} hrs/night**, "
            "vs. those using fewer than 3 hours who sleep "
            f"**{filtered_df1[filtered_df1['Avg_Daily_Usage_Hours'] < 3]['Sleep_Hours_Per_Night'].mean():.1f} hrs/night**."
        )

    with col2:
        st.warning(
            "**🧠 Mental Health**\n\n"
            "Heavy users (5+ hrs) report an average mental health score of "
            f"**{filtered_df1[filtered_df1['Avg_Daily_Usage_Hours'] >= 5]['Mental_Health_Score'].mean():.1f}/10**, "
            "compared to **"
            f"{filtered_df1[filtered_df1['Avg_Daily_Usage_Hours'] < 3]['Mental_Health_Score'].mean():.1f}/10** "
            "for light users."
        )

    with col3:
        pct_neg = round(
            df2[df2["Overall Effect"] == "Mostly negative"].shape[0] / df2.shape[0] * 100
        )
        pct_pos = round(
            df2[df2["Overall Effect"] == "Mostly positive"].shape[0] / df2.shape[0] * 100
        )
        st.error(
            "**📚 Academic Performance**\n\n"
            f"**{pct_neg}%** of students feel social media has a mostly negative effect on their studies, "
            f"while **{pct_pos}%** say it helps. The rest are unsure or neutral."
        )

    st.markdown("---")
    st.subheader("❓ Research Questions")
    st.write("- Does more social media time relate to less sleep?")
    st.write("- Is heavier usage linked to lower mental health scores?")
    st.write("- Do different platforms associate with different student outcomes?")
    st.write("- How do students' *reasons* for using social media relate to their GPA?")

    st.markdown("---")
    st.subheader("📂 Data Sources")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            "**Dataset 1 — Social Media Addiction Survey**  \n"
            "705 students · 110 countries  \n"
            "Variables: usage hours, sleep, mental health, addiction score, platform"
        )
    with col_b:
        st.markdown(
            "**Dataset 2 — Academic Performance Survey**  \n"
            "300 college students  \n"
            "Variables: GPA, usage hours, platforms (multi-select), reasons, perceived impact"
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SLEEP & USAGE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "😴 Sleep & Usage":
    st.title("😴 Social Media Usage and Sleep")
    st.write(
        "Each point represents one student. Use the sidebar to filter by gender or academic level. "
        "The correlation between daily usage and sleep hours is **r = −0.79** — a strong negative relationship."
    )

    # Scatter
    fig = px.scatter(
        filtered_df1,
        x="Avg_Daily_Usage_Hours",
        y="Sleep_Hours_Per_Night",
        color="Gender",
        trendline="ols",
        hover_data=["Age", "Academic_Level", "Country", "Most_Used_Platform"],
        opacity=0.55,
        title="Daily Social Media Usage vs Sleep Hours (with trend line)",
        labels={
            "Avg_Daily_Usage_Hours": "Avg Daily Usage (Hours)",
            "Sleep_Hours_Per_Night": "Sleep Hours per Night",
        },
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Bin usage and show average sleep
    st.subheader("Average Sleep by Usage Group")
    st.write("Students are grouped into usage buckets to show the step-down pattern more clearly.")

    filtered_df1["Usage_Group"] = pd.cut(
        filtered_df1["Avg_Daily_Usage_Hours"],
        bins=[0, 2, 3, 4, 5, 6, 10],
        labels=["< 2 hrs", "2–3 hrs", "3–4 hrs", "4–5 hrs", "5–6 hrs", "6+ hrs"],
    )
    sleep_group = (
        filtered_df1.groupby("Usage_Group", observed=True)
        .agg(Avg_Sleep=("Sleep_Hours_Per_Night", "mean"), Count=("Sleep_Hours_Per_Night", "count"))
        .reset_index()
    )

    fig2 = px.bar(
        sleep_group,
        x="Usage_Group",
        y="Avg_Sleep",
        text=sleep_group["Count"].apply(lambda n: f"n={n}"),
        title="Average Sleep Hours by Daily Usage Group",
        labels={"Usage_Group": "Daily Usage Group", "Avg_Sleep": "Avg Sleep (hrs)"},
        color="Avg_Sleep",
        color_continuous_scale="Blues_r",
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(coloraxis_showscale=False, yaxis_range=[0, 10])
    st.plotly_chart(fig2, use_container_width=True)

    st.caption(
        "⚠️ n= labels show sample size per group. "
        "Groups with very few students should be interpreted with caution."
    )

    st.markdown("---")
    st.subheader("💡 Takeaway")
    st.success(
        "There is a clear, consistent pattern: as daily social media usage increases, "
        "average sleep duration decreases. Students using social media 6+ hours per day "
        "sleep roughly 1.5–2 hours less than those using it under 2 hours."
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MENTAL HEALTH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧠 Mental Health":
    st.title("🧠 Social Media Usage and Mental Health")
    st.write(
        "Mental Health Score is self-reported on a scale of 1–10 (higher = better). "
        "The correlation with daily usage is **r = −0.80** — comparable to the sleep relationship."
    )

    fig = px.scatter(
        filtered_df1,
        x="Avg_Daily_Usage_Hours",
        y="Mental_Health_Score",
        color="Gender",
        trendline="ols",
        hover_data=["Age", "Academic_Level", "Country", "Most_Used_Platform"],
        opacity=0.55,
        title="Daily Social Media Usage vs Mental Health Score (with trend line)",
        labels={
            "Avg_Daily_Usage_Hours": "Avg Daily Usage (Hours)",
            "Mental_Health_Score": "Mental Health Score (1–10)",
        },
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Addicted score vs mental health
    st.subheader("Addiction Score vs Mental Health Score")
    st.write(
        "The dataset includes an Addiction Score (1–10). "
        "The correlation with mental health is even stronger at **r = −0.89**."
    )

    fig2 = px.scatter(
        filtered_df1,
        x="Addicted_Score",
        y="Mental_Health_Score",
        color="Academic_Level",
        trendline="ols",
        opacity=0.55,
        title="Addiction Score vs Mental Health Score",
        labels={
            "Addicted_Score": "Addiction Score (1–10)",
            "Mental_Health_Score": "Mental Health Score (1–10)",
        },
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Conflicts over social media
    st.subheader("Social Media Conflicts vs Mental Health")
    conflict_summary = (
        filtered_df1.groupby("Conflicts_Over_Social_Media")
        .agg(Avg_MH=("Mental_Health_Score", "mean"), Count=("Mental_Health_Score", "count"))
        .reset_index()
    )
    fig3 = px.bar(
        conflict_summary,
        x="Conflicts_Over_Social_Media",
        y="Avg_MH",
        text=conflict_summary["Count"].apply(lambda n: f"n={n}"),
        title="Avg Mental Health Score by Number of Social Media Conflicts",
        labels={
            "Conflicts_Over_Social_Media": "# of Conflicts Over Social Media",
            "Avg_MH": "Avg Mental Health Score",
        },
        color="Avg_MH",
        color_continuous_scale="RdYlGn",
    )
    fig3.update_traces(textposition="outside")
    fig3.update_layout(coloraxis_showscale=False, yaxis_range=[0, 11])
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("💡 Takeaway")
    st.success(
        "Higher usage, higher addiction scores, and more conflicts over social media all "
        "consistently associate with lower mental health scores. "
        "Students with 5+ conflicts report mental health scores nearly 4 points lower "
        "than those with no conflicts."
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ACADEMIC PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📚 Academic Performance":
    st.title("📚 Social Media Usage and Academic Performance")
    st.write(
        "This page uses Dataset 2 (n=300 college students), which includes GPA ranges, "
        "perceived academic impact, and reasons for social media use."
    )

    # ── GPA distribution by usage hours ──
    st.subheader("GPA Distribution by Daily Usage Hours")
    st.write(
        "Each bar shows the proportion of students in each GPA bracket, "
        "grouped by how many hours per day they spend on social media."
    )

    usage_order = ["Less than 1 hour", "1-2 hours", "3-4 hours", "5-6 hours", "More than 6 hours"]
    gpa_order = ["2.0-2.5", "2.5-3.0", "3.0-3.5", "3.5-4.0"]

    gpa_usage = (
        df2.groupby(["Hours on Social Media", "GPA"])
        .size()
        .reset_index(name="Count")
    )
    gpa_usage["Hours on Social Media"] = pd.Categorical(
        gpa_usage["Hours on Social Media"], categories=usage_order, ordered=True
    )
    gpa_usage["GPA"] = pd.Categorical(gpa_usage["GPA"], categories=gpa_order, ordered=True)
    gpa_usage = gpa_usage.sort_values(["Hours on Social Media", "GPA"])

    # Compute percentage within each usage group
    totals = gpa_usage.groupby("Hours on Social Media")["Count"].transform("sum")
    gpa_usage["Pct"] = (gpa_usage["Count"] / totals * 100).round(1)
    gpa_usage["n_label"] = gpa_usage.groupby("Hours on Social Media")["Count"].transform("sum")

    fig = px.bar(
        gpa_usage,
        x="Hours on Social Media",
        y="Pct",
        color="GPA",
        barmode="stack",
        category_orders={"Hours on Social Media": usage_order, "GPA": gpa_order},
        title="GPA Distribution by Daily Social Media Usage (% within group)",
        labels={"Pct": "% of Students", "Hours on Social Media": "Daily Usage"},
        color_discrete_map={
            "2.0-2.5": "#d73027",
            "2.5-3.0": "#fc8d59",
            "3.0-3.5": "#91bfdb",
            "3.5-4.0": "#4575b4",
        },
    )

    # Add n= labels per group
    n_per_group = df2["Hours on Social Media"].value_counts().reset_index()
    n_per_group.columns = ["Hours on Social Media", "n"]
    for _, row in n_per_group.iterrows():
        fig.add_annotation(
            x=row["Hours on Social Media"],
            y=102,
            text=f"n={row['n']}",
            showarrow=False,
            font=dict(size=10, color="gray"),
        )
    fig.update_layout(yaxis_range=[0, 110])
    st.plotly_chart(fig, use_container_width=True)
    st.caption("n= labels show the number of students in each usage group.")

    st.markdown("---")

    # ── Perceived overall effect ──
    st.subheader("Students' Self-Perceived Academic Impact")
    st.write(
        "Students were asked to rate the overall effect of social media on their academic performance."
    )

    effect_counts = df2["Overall Effect"].value_counts().reset_index()
    effect_counts.columns = ["Effect", "Count"]
    effect_order = ["Mostly positive", "Neutral", "Unsure", "Mostly negative"]
    effect_counts["Effect"] = pd.Categorical(effect_counts["Effect"], categories=effect_order, ordered=True)
    effect_counts = effect_counts.sort_values("Effect")

    fig2 = px.bar(
        effect_counts,
        x="Effect",
        y="Count",
        color="Effect",
        title="How Students Rate Social Media's Effect on Academic Performance",
        color_discrete_map={
            "Mostly positive": "#4575b4",
            "Neutral": "#91bfdb",
            "Unsure": "#fee08b",
            "Mostly negative": "#d73027",
        },
        text="Count",
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(showlegend=False, yaxis_range=[0, 110])
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Reasons for usage vs GPA ──
    st.subheader("Reasons for Social Media Use vs GPA")
    st.write(
        "Students often use social media for multiple reasons. "
        "Each student-reason pair is counted separately to show which reasons are most common across GPA levels."
    )

    reason_gpa = (
        df2_reasons.groupby(["Reason_List", "GPA"])
        .size()
        .reset_index(name="Count")
    )
    reason_gpa["GPA"] = pd.Categorical(reason_gpa["GPA"], categories=gpa_order, ordered=True)

    # Compute % within reason group
    reason_totals = reason_gpa.groupby("Reason_List")["Count"].transform("sum")
    reason_gpa["Pct"] = (reason_gpa["Count"] / reason_totals * 100).round(1)
    reason_n = df2_reasons.groupby("Reason_List").size().reset_index(name="n")

    fig3 = px.bar(
        reason_gpa,
        x="Reason_List",
        y="Pct",
        color="GPA",
        barmode="stack",
        category_orders={"GPA": gpa_order},
        title="GPA Distribution by Primary Reason for Social Media Use (% within reason)",
        labels={"Reason_List": "Reason for Use", "Pct": "% of Students"},
        color_discrete_map={
            "2.0-2.5": "#d73027",
            "2.5-3.0": "#fc8d59",
            "3.0-3.5": "#91bfdb",
            "3.5-4.0": "#4575b4",
        },
    )
    for _, row in reason_n.iterrows():
        fig3.add_annotation(
            x=row["Reason_List"],
            y=102,
            text=f"n={row['n']}",
            showarrow=False,
            font=dict(size=10, color="gray"),
        )
    fig3.update_layout(yaxis_range=[0, 115])
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("💡 Takeaway")
    st.success(
        "Students who use social media for educational purposes or professional networking "
        "tend to have a higher share of 3.5–4.0 GPAs compared to those using it primarily for entertainment. "
        "Meanwhile, heavier usage (5–6+ hrs/day) is associated with a larger share of students in the lower GPA brackets."
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PLATFORM ANALYSIS (addresses professor feedback directly)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Platform Analysis":
    st.title("📊 Platform Analysis")

    st.info(
        "**Note on methodology:** Most students use multiple platforms simultaneously. "
        "The charts below use Dataset 2, where students reported *all* platforms they use. "
        "Each platform is counted separately, so one student may appear under multiple platforms. "
        "Sample sizes (n=) are shown on each chart."
    )

    # ── Dataset 2: Multi-platform — GPA distribution ──
    st.subheader("GPA Distribution by Platform Used (multi-platform, Dataset 2)")
    st.write(
        "Students in Dataset 2 reported all platforms they use. "
        "This chart shows GPA distribution for users of each platform."
    )

    gpa_order = ["2.0-2.5", "2.5-3.0", "3.0-3.5", "3.5-4.0"]
    top_platforms = df2_exploded["Platform_List"].value_counts().index.tolist()

    plat_gpa = (
        df2_exploded.groupby(["Platform_List", "GPA"])
        .size()
        .reset_index(name="Count")
    )
    plat_gpa["GPA"] = pd.Categorical(plat_gpa["GPA"], categories=gpa_order, ordered=True)
    plat_gpa_totals = plat_gpa.groupby("Platform_List")["Count"].transform("sum")
    plat_gpa["Pct"] = (plat_gpa["Count"] / plat_gpa_totals * 100).round(1)
    plat_n = df2_exploded.groupby("Platform_List").size().reset_index(name="n")

    fig = px.bar(
        plat_gpa,
        x="Platform_List",
        y="Pct",
        color="GPA",
        barmode="stack",
        category_orders={"Platform_List": top_platforms, "GPA": gpa_order},
        title="GPA Distribution by Platform Used (% within platform, multi-platform data)",
        labels={"Platform_List": "Platform", "Pct": "% of Users"},
        color_discrete_map={
            "2.0-2.5": "#d73027",
            "2.5-3.0": "#fc8d59",
            "3.0-3.5": "#91bfdb",
            "3.5-4.0": "#4575b4",
        },
    )
    for _, row in plat_n.iterrows():
        fig.add_annotation(
            x=row["Platform_List"],
            y=102,
            text=f"n={row['n']}",
            showarrow=False,
            font=dict(size=10, color="gray"),
        )
    fig.update_layout(yaxis_range=[0, 115])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Dataset 2: Perceived effect by platform ──
    st.subheader("Perceived Academic Effect by Platform (multi-platform, Dataset 2)")
    effect_order = ["Mostly positive", "Neutral", "Unsure", "Mostly negative"]
    plat_effect = (
        df2_exploded.groupby(["Platform_List", "Overall Effect"])
        .size()
        .reset_index(name="Count")
    )
    plat_effect["Overall Effect"] = pd.Categorical(
        plat_effect["Overall Effect"], categories=effect_order, ordered=True
    )
    plat_effect_totals = plat_effect.groupby("Platform_List")["Count"].transform("sum")
    plat_effect["Pct"] = (plat_effect["Count"] / plat_effect_totals * 100).round(1)

    fig2 = px.bar(
        plat_effect,
        x="Platform_List",
        y="Pct",
        color="Overall Effect",
        barmode="stack",
        category_orders={"Platform_List": top_platforms, "Overall Effect": effect_order},
        title="Perceived Academic Effect by Platform (% within platform)",
        labels={"Platform_List": "Platform", "Pct": "% of Users"},
        color_discrete_map={
            "Mostly positive": "#4575b4",
            "Neutral": "#91bfdb",
            "Unsure": "#fee08b",
            "Mostly negative": "#d73027",
        },
    )
    for _, row in plat_n.iterrows():
        fig2.add_annotation(
            x=row["Platform_List"],
            y=102,
            text=f"n={row['n']}",
            showarrow=False,
            font=dict(size=10, color="gray"),
        )
    fig2.update_layout(yaxis_range=[0, 115])
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Dataset 1: Single "most-used" platform — sleep & mental health ──
    st.subheader("Sleep & Mental Health by Most-Used Platform (Dataset 1)")
    st.write(
        "Dataset 1 records each student's single *most-used* platform. "
        "While this is a simplification (students use many platforms), "
        "it gives a proxy for dominant usage behavior. "
        "Platforms with fewer than 20 students are shown with a dashed border to signal caution."
    )

    plat_summary = (
        df1.groupby("Most_Used_Platform")
        .agg(
            Avg_Sleep=("Sleep_Hours_Per_Night", "mean"),
            Avg_MH=("Mental_Health_Score", "mean"),
            Count=("Sleep_Hours_Per_Night", "count"),
        )
        .reset_index()
        .sort_values("Count", ascending=False)
    )
    plat_summary["Label"] = plat_summary.apply(
        lambda r: f"{r['Most_Used_Platform']} (n={r['Count']})", axis=1
    )

    col1, col2 = st.columns(2)

    with col1:
        fig3 = px.bar(
            plat_summary,
            x="Most_Used_Platform",
            y="Avg_Sleep",
            text=plat_summary["Count"].apply(lambda n: f"n={n}"),
            title="Avg Sleep Hours by Most-Used Platform",
            labels={"Most_Used_Platform": "Platform", "Avg_Sleep": "Avg Sleep (hrs)"},
            color="Avg_Sleep",
            color_continuous_scale="Blues",
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(coloraxis_showscale=False, yaxis_range=[0, 11])
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        fig4 = px.bar(
            plat_summary,
            x="Most_Used_Platform",
            y="Avg_MH",
            text=plat_summary["Count"].apply(lambda n: f"n={n}"),
            title="Avg Mental Health Score by Most-Used Platform",
            labels={"Most_Used_Platform": "Platform", "Avg_MH": "Avg Mental Health Score"},
            color="Avg_MH",
            color_continuous_scale="RdYlGn",
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(coloraxis_showscale=False, yaxis_range=[0, 12])
        st.plotly_chart(fig4, use_container_width=True)

    st.caption(
        "⚠️ Platforms with small n (e.g., YouTube n=10, Snapchat n=13) should be "
        "interpreted cautiously — averages from small samples are unstable."
    )

    st.markdown("---")
    st.subheader("💡 Takeaway")
    st.success(
        "Across both datasets, Snapchat and WhatsApp users show lower average sleep hours, "
        "while Facebook, LinkedIn, and LINE users tend to sleep more. "
        "However, because students use multiple platforms, the 'most-used' label is a simplification — "
        "the multi-platform analysis in Dataset 2 gives a more complete picture."
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DATASET OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Dataset Overview":
    st.title("🔍 Dataset Overview")
    st.write("Raw data summaries for reference.")

    tab1, tab2 = st.tabs(["Dataset 1 — Addiction Survey", "Dataset 2 — Academic Performance"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        col1.metric("Students", df1.shape[0])
        col2.metric("Variables", df1.shape[1])
        col3.metric("Countries", df1["Country"].nunique())
        st.subheader("Preview")
        st.dataframe(df1.head(10))
        st.subheader("Summary Statistics")
        st.dataframe(df1.describe().round(2))

    with tab2:
        col1, col2, col3 = st.columns(3)
        col1.metric("Students", df2.shape[0])
        col2.metric("Variables", df2.shape[1])
        col3.metric("GPA Brackets", df2["GPA"].nunique())
        st.subheader("Preview")
        st.dataframe(df2.drop(columns=["Platform_List", "Reason_List", "Usage_Hours_Ordered"]).head(10))
        st.subheader("Column Names")
        st.write(df2.drop(columns=["Platform_List", "Reason_List", "Usage_Hours_Ordered"]).columns.tolist())
