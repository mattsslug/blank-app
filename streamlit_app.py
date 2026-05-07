import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="QA Score Dashboard", layout="wide")

st.title("QA Score Dashboard")
st.write(
    "Upload your QA Excel file to analyze QA scores by Quality Assurance End Date."
)

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx", "xls"]
)

if uploaded_file:
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file)

        # Required columns
        score_column = "QA Score "
        date_column = "Quality Assurance End Date"
        engine_model_column = "Engine Model"

        # Validate columns
        missing_columns = [
            col for col in [score_column, date_column, engine_model_column]
            if col not in df.columns
        ]

        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
        else:
            # Clean data
            df[score_column] = pd.to_numeric(df[score_column], errors="coerce")
            df[date_column] = pd.to_datetime(df[date_column], errors="coerce")

            filtered_df = df.dropna(subset=[score_column, date_column])

            # Sidebar slicer for Engine Model
            st.sidebar.header("Filters")

            engine_models = sorted(
                filtered_df[engine_model_column]
                .dropna()
                .astype(str)
                .unique()
            )

            selected_models = st.sidebar.multiselect(
                "Select Engine Model",
                options=engine_models,
                default=engine_models
            )

            # Apply filter
            filtered_df = filtered_df[
                filtered_df[engine_model_column]
                .astype(str)
                .isin(selected_models)
            ]

            # Create date-only column
            filtered_df["QA Date"] = filtered_df[date_column].dt.date

            st.subheader("Filtered Raw Data")
            st.dataframe(filtered_df, use_container_width=True)

            # KPI Metrics
            avg_score = filtered_df[score_column].mean()
            max_score = filtered_df[score_column].max()
            min_score = filtered_df[score_column].min()

            col1, col2, col3 = st.columns(3)

            col1.metric("Average QA Score", f"{avg_score:.2f}")
            col2.metric("Highest QA Score", f"{max_score:.2f}")
            col3.metric("Lowest QA Score", f"{min_score:.2f}")

            st.divider()

            # Group by date
            date_summary = (
                filtered_df.groupby("QA Date")[score_column]
                .mean()
                .reset_index()
                .sort_values(by="QA Date")
            )

            # Line chart
            st.subheader("Average QA Score by Date")

            fig_line = px.line(
                date_summary,
                x="QA Date",
                y=score_column,
                markers=True,
                title="QA Score Trend by Date"
            )

            fig_line.update_layout(
                xaxis_title="Quality Assurance End Date",
                yaxis_title="Average QA Score"
            )

            st.plotly_chart(fig_line, use_container_width=True)

            # Daily breakdown table
            st.subheader("Daily QA Score Summary")
            st.dataframe(date_summary, use_container_width=True)

            # Distribution chart
            st.subheader("QA Score Distribution")

            fig_hist = px.histogram(
                filtered_df,
                x=score_column,
                nbins=20,
                title="Distribution of QA Scores"
            )

            st.plotly_chart(fig_hist, use_container_width=True)

            # Download summary
            csv = date_summary.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Date Summary CSV",
                data=csv,
                file_name="qa_score_by_date_summary.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error reading file: {e}")

else:
    st.info("Please upload an Excel file to begin.")

st.markdown("---")
st.caption("Built with Streamlit")
