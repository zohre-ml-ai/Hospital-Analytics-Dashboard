import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
# ======================================
# Page Settings
# ======================================
st.set_page_config(
    page_title="Hospital Dashboard",
    page_icon="🏥",
    layout="wide"
)
# ======================================
# Load Data
# ======================================
@st.cache_data
def load_data():

    df = pd.read_csv("patients_sample_500.csv")

    df["admission_date"] = pd.to_datetime(df["admission_date"])
    df["discharge_date"] = pd.to_datetime(df["discharge_date"])

    df["length_of_stay"] = (
        df["discharge_date"] -
        df["admission_date"]
    ).dt.days

    return df
# ======================================
# App Start (IMPORTANT)
# ======================================
df = load_data()

st.title("🏥 Hospital Dashboard")

st.write(df.head())
# ======================================
# Sidebar Filters
# ======================================
st.sidebar.header(
    "Dashboard Filters"
)
#=======departement select========================
selected_departments = st.sidebar.multiselect(
    "Select Department",

    options=df["department"].unique(),

    default=df["department"].unique()
)
#======date filter====================
st.sidebar.subheader(
    "Date Filter"
)
start_date = st.sidebar.date_input(

    "Start Date",

    value=df["admission_date"].min()

)
end_date = st.sidebar.date_input(

    "End Date",

    value=df["admission_date"].max()

)
#=====filtered_df============================
filtered_df = df[

    (df["department"].isin(
        selected_departments
    ))

    &

    (
        df["admission_date"].dt.date
        >=
        start_date
    )

    &

    (
        df["admission_date"].dt.date
        <=
        end_date
    )

]
#=====filter test================================
st.subheader(
    "Filtered Dataset"
)

st.write(

    f"Showing {len(filtered_df)} records"

)

st.dataframe(

    filtered_df.head(20)

)
# ======================================
# KPI Calculations
# ======================================
patients = len(filtered_df)

revenue = filtered_df["revenue"].sum()

cost = filtered_df["cost"].sum()

profit = revenue - cost

if revenue > 0:

    profit_margin = (
        profit
        /
        revenue
    ) * 100

else:

    profit_margin = 0


alos = filtered_df["length_of_stay"].mean()

readmission_rate = (
    filtered_df["readmission_flag"].mean()
) * 100

mortality_rate = (
    filtered_df["death_flag"].mean()
) * 100
# ======================================
# Dashboard Title
# ======================================
st.markdown("---")

st.title(
    "🏥 Hospital Executive Dashboard"
)
# ======================================
# KPI Cards Row 1
# ======================================
col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Patients",
        f"{patients:,}"
    )

with col2:

    st.metric(
        "Revenue",
        f"${revenue:,.0f}"
    )

with col3:

    st.metric(
        "Profit",
        f"${profit:,.0f}"
    )
    # ======================================
# KPI Cards Row 2
# ======================================
col4, col5, col6 = st.columns(3)

with col4:

    st.metric(
        "ALOS",
        f"{alos:.2f} Days"
    )

with col5:

    st.metric(
        "Readmission Rate",
        f"{readmission_rate:.2f}%"
    )

with col6:

    st.metric(
        "Mortality Rate",
        f"{mortality_rate:.2f}%"
    )
    st.markdown("---")

st.metric(
    "Profit Margin",
    f"{profit_margin:.2f}%"
)
# ======================================
# Department Financial Analysis
# ======================================
department_financial = (
    filtered_df
    .groupby("department")
    .agg(
        revenue=("revenue","sum"),
        cost=("cost","sum")
    )
    .reset_index()
)

st.markdown("---")

st.subheader(
    "Revenue vs Cost by Department"
)
# ======================================
# Department Summary
# ======================================
department_summary = (

    filtered_df

    .groupby("department")

    .agg(

        patients=("patient_id","count"),

        revenue=("revenue","sum"),

        cost=("cost","sum"),

        alos=("length_of_stay","mean"),

        readmission_rate=("readmission_flag","mean"),

        mortality_rate=("death_flag","mean")

    )

)

department_summary["profit"] = (

    department_summary["revenue"]

    -

    department_summary["cost"]

)

department_summary["readmission_rate"] *= 100

department_summary["mortality_rate"] *= 100
#==========================plot fig===================
fig = px.bar(

    department_financial,

    x="department",

    y=["revenue","cost"],

    barmode="group",

    title="Revenue vs Cost by Department"

)

st.plotly_chart(
    fig,
    use_container_width=True
)
fig_readmission = px.bar(

    department_summary.reset_index(),

    x="department",

    y="readmission_rate",

    text="readmission_rate",

    title="Readmission Rate by Department"

)

st.plotly_chart(
    fig_readmission,
    use_container_width=True
)
fig_mortality = px.bar(

    department_summary.reset_index(),

    x="department",

    y="mortality_rate",

    text="mortality_rate",

    title="Mortality Rate by Department"

)

st.plotly_chart(
    fig_mortality,
    use_container_width=True
)
# ======================================
# Department Ranking
# ======================================
score_df = department_summary.copy()


score_df["profit_score"] = (

    score_df["profit"]

    /

    score_df["profit"].max()

) * 100


score_df["alos_score"] = (

    1 -

    (

        score_df["alos"]

        /

        score_df["alos"].max()

    )

) * 100


score_df["readmission_score"] = (

    1 -

    (

        score_df["readmission_rate"]

        /

        score_df["readmission_rate"].max()

    )

) * 100


score_df["mortality_score"] = (

    1 -

    (

        score_df["mortality_rate"]

        /

        score_df["mortality_rate"].max()

    )

) * 100


score_df["weighted_score"] = (

    score_df["mortality_score"] * 0.40

    +

    score_df["readmission_score"] * 0.30

    +

    score_df["profit_score"] * 0.20

    +

    score_df["alos_score"] * 0.10

)


score_df = score_df.sort_values(

    by="weighted_score",

    ascending=False

)

score_df["rank"] = range(

    1,

    len(score_df)+1

)

score_df.index.name = "department"
#================= Department Ranking Chart =========================
st.markdown("---")

st.subheader(
    "Department Performance Ranking"
)

fig_rank = px.bar(

    score_df.reset_index(),

    x="department",

    y="weighted_score",

    text="weighted_score",

    title="Department Performance Ranking"

)

st.plotly_chart(

    fig_rank,

    use_container_width=True

)
#================= Department Ranking Table =========================
st.markdown("---")

st.header(
    "🏆 Department Ranking"
)

st.dataframe(

    score_df[

        [

            "rank",

            "weighted_score",

            "profit",

            "alos",

            "readmission_rate",

            "mortality_rate"

        ]

    ].round(2)

)
# ======================================
# Management Alerts
# ======================================
st.markdown("---")

st.header(
    "🚨 Management Alerts"
)

if mortality_rate > 2:

    st.error(
        f"Mortality Rate is High ({mortality_rate:.2f}%)"
    )

else:

    st.success(
        f"Mortality Rate is Acceptable ({mortality_rate:.2f}%)"
    )


if readmission_rate > 10:

    st.warning(
        f"Readmission Rate is High ({readmission_rate:.2f}%)"
    )

else:

    st.success(
        f"Readmission Rate is Acceptable ({readmission_rate:.2f}%)"
    )


if alos > 8:

    st.warning(
        f"ALOS is High ({alos:.2f} Days)"
    )

else:

    st.success(
        f"ALOS is Acceptable ({alos:.2f} Days)"
    )
#========================بهترین و بدترین دپارتمان======================
best_department = score_df.index[0]

worst_department = score_df.index[-1]


st.success(

    f"Best Department: {best_department}"

)


st.error(

    f"Worst Department: {worst_department}"

)
# ======================================
# Doctor Analysis
# ======================================
doctor_summary = (

    filtered_df

    .groupby("doctor")

    .agg(

        patients=("patient_id","count"),

        revenue=("revenue","sum"),

        cost=("cost","sum"),

        satisfaction=("satisfaction_score","mean"),

        readmission_rate=("readmission_flag","mean"),

        mortality_rate=("death_flag","mean")

    )

)


doctor_summary["profit"] = (

    doctor_summary["revenue"]

    -

    doctor_summary["cost"]

)


doctor_summary["readmission_rate"] *= 100

doctor_summary["mortality_rate"] *= 100


st.markdown("---")

st.header(

    "👨‍⚕️ Doctor Performance"

)


st.dataframe(

    doctor_summary.round(2)

)

doctor_rank = doctor_summary.copy()


doctor_rank["profit_score"] = (

    doctor_rank["profit"]

    /

    doctor_rank["profit"].max()

) * 100


doctor_rank["satisfaction_score_norm"] = (

    doctor_rank["satisfaction"]

    /

    doctor_rank["satisfaction"].max()

) * 100


doctor_rank["readmission_score"] = (

    1 -

    (

        doctor_rank["readmission_rate"]

        /

        doctor_rank["readmission_rate"].max()

    )

) * 100


doctor_rank["mortality_score"] = (

    1 -

    (

        doctor_rank["mortality_rate"]

        /

        doctor_rank["mortality_rate"].max()

    )

) * 100


doctor_rank["overall_score"] = (

    doctor_rank["mortality_score"] * 0.40

    +

    doctor_rank["readmission_score"] * 0.30

    +

    doctor_rank["satisfaction_score_norm"] * 0.20

    +

    doctor_rank["profit_score"] * 0.10

)


doctor_rank = doctor_rank.sort_values(

    by="overall_score",

    ascending=False

)


doctor_rank["rank"] = range(

    1,

    len(doctor_rank)+1

)
#=========نمایش پزشکان برتر=========================
st.markdown("---")

st.header(

    "🥇 Top Doctors"

)


st.dataframe(

    doctor_rank.head(10)[

        [

            "rank",

            "patients",

            "profit",

            "satisfaction",

            "readmission_rate",

            "mortality_rate",

            "overall_score"

        ]

    ].round(2)

)

st.markdown("---")

st.header(

    "🥇 Top Doctors"

)


st.dataframe(

    doctor_rank.head(10)[

        [

            "rank",

            "patients",

            "profit",

            "satisfaction",

            "readmission_rate",

            "mortality_rate",

            "overall_score"

        ]

    ].round(2)

)
#===================================insurance summary======================
insurance_summary = (
    filtered_df
    .groupby("insurance_type")
    .agg(
        patients=("patient_id","count"),
        revenue=("revenue","sum"),
        cost=("cost","sum"),
        satisfaction=("satisfaction_score","mean"),
        alos=("length_of_stay","mean"),
        readmission_rate=("readmission_flag","mean"),
        mortality_rate=("death_flag","mean")
    )
)

insurance_summary["profit"] = (
    insurance_summary["revenue"]
    -
    insurance_summary["cost"]
)

insurance_summary["readmission_rate"] *= 100
insurance_summary["mortality_rate"] *= 100

insurance_summary.index.name = "insurance_type"
#=====جدول بیمه ها====================
st.markdown("---")

st.header("💳 Insurance Analysis")

st.dataframe(

    insurance_summary.round(2)

)
#=======نمودار سود بیمه ها================
fig_insurance = px.bar(

    insurance_summary.reset_index(),

    x="insurance_type",

    y="profit",

    title="Profit by Insurance Type"

)

st.plotly_chart(

    fig_insurance,

    use_container_width=True

)
#=======================نمودار توزیع بیماران بیمه ها =====================
fig_insurance_patient = px.pie(

    insurance_summary.reset_index(),

    names="insurance_type",

    values="patients",

    hole=0.4,

    title="Patient Distribution by Insurance"

)

st.plotly_chart(

    fig_insurance_patient,

    use_container_width=True

)
# ======================================
# Monthly Admissions Trend
# ======================================
trend_df = (

    filtered_df

    .groupby(

        filtered_df["admission_date"]

        .dt.to_period("M")

    )

    .size()

    .reset_index(name="patients")

)


trend_df["admission_date"] = (

    trend_df["admission_date"]

    .astype(str)

)
#================نمودار روند پذیرش=============================
st.markdown("---")

st.header(

    "📈 Monthly Admission Trend"

)


fig_trend = px.line(

    trend_df,

    x="admission_date",

    y="patients",

    markers=True

)

st.plotly_chart(

    fig_trend,

    use_container_width=True

)

monthly_revenue = (

    filtered_df

    .groupby(

        filtered_df["admission_date"]

        .dt.to_period("M")

    )["revenue"]

    .sum()

    .reset_index()

)


monthly_revenue["admission_date"] = (

    monthly_revenue["admission_date"]

    .astype(str)

)
#==========نمودار درامد ماهانه ===============
fig_monthly_revenue = px.line(

    monthly_revenue,

    x="admission_date",

    y="revenue",

    title="Monthly Revenue Trend"

)

st.plotly_chart(

    fig_monthly_revenue,

    use_container_width=True

)
#========روند سود ماهانه=========================
monthly_profit = (

    filtered_df

    .groupby(

        filtered_df["admission_date"]

        .dt.to_period("M")

    )

    .agg(

        revenue=("revenue","sum"),

        cost=("cost","sum")

    )

    .reset_index()

)

monthly_profit["profit"] = (

    monthly_profit["revenue"]

    -

    monthly_profit["cost"]

)


monthly_profit["admission_date"] = (

    monthly_profit["admission_date"]

    .astype(str)

)
#==================نمودار سود ماهانه =================
fig_profit = px.line(

    monthly_profit,

    x="admission_date",

    y="profit",

    markers=True,

    title="Monthly Profit Trend"

)

st.plotly_chart(

    fig_profit,

    use_container_width=True

)
# ======================================
# Export Excel Report
# ======================================
st.markdown("---")

st.header("📥 Download Reports")


output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="openpyxl"
) as writer:

    department_summary.to_excel(
        writer,
        sheet_name="Departments"
    )

    doctor_rank.to_excel(
        writer,
        sheet_name="Doctors"
    )

    insurance_summary.to_excel(
        writer,
        sheet_name="Insurance"
    )

    score_df.to_excel(
        writer,
        sheet_name="Department Ranking"
    )


excel_data = output.getvalue()


st.download_button(

    label="📥 Download Excel Report",

    data=excel_data,

    file_name="Hospital_Dashboard_Report.xlsx",

    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

)

#====بهترین دپارتمان===================
best_department = score_df.index[0]
#=================بهترین پزشک============================
best_doctor = doctor_rank.index[0]
# ======================================
# Executive Summary
# ======================================
st.markdown("---")

st.header(
    "📋 Executive Summary"
)

st.write(

    f"""
### Key Insights

• Total Patients : {patients}

• Total Revenue : ${revenue:,.0f}

• Total Profit : ${profit:,.0f}

• Profit Margin : {profit_margin:.2f} %

• Average Length of Stay : {alos:.2f} days

• Readmission Rate : {readmission_rate:.2f} %

• Mortality Rate : {mortality_rate:.2f} %

• Best Department : {best_department}

• Best Doctor : {best_doctor}

"""
)
#=====Footer===================
st.markdown("---")

st.caption(

    "Hospital Dashboard | Developed with Python, Pandas, Plotly and Streamlit"

)
