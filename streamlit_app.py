import streamlit as st
import pandas as pd
import my_functions
import time
import streamlit as st
#import plotly.graph_objs as go
import pandas as pd
#import plotly.express as px
import warnings
from PIL import Image
import datetime as datetime
from streamlit_option_menu import option_menu
from scipy import stats
import xlrd as xlrd

st.set_page_config(page_title="", page_icon="",
                   initial_sidebar_state="expanded", menu_items={"About": "Rev 0 - M.Serag"}, layout="wide")

col1, col2, col3, col4 = st.columns(4, gap="large")
with col1:
    uploaded_file_time = st.file_uploader("Time and Cost", type="XLS", accept_multiple_files=False, key="Time", help=None,
                                          on_change=None, args=None,
                                          kwargs=None, disabled=False, label_visibility="visible")
with col2:
    uploaded_file_docs = st.file_uploader("Documents", type="XLSX", accept_multiple_files=False, key="Doc", help=None,
                                          on_change=None, args=None,
                                          kwargs=None, disabled=False, label_visibility="visible")
with col3:
    uploaded_file_invoices = st.file_uploader("Invoicing", type="XLS", accept_multiple_files=False, key="invoice", help=None,
                                          on_change=None, args=None,
                                          kwargs=None, disabled=False, label_visibility="visible")
with col4:
    st.write()

if uploaded_file_time is not None:
    df = my_functions.get_data_from_excel(uploaded_file_time)
    df.dropna(how='all', axis=1, inplace=True)
if uploaded_file_docs is not None:
    df1 = my_functions.get_data_from_excel(uploaded_file_docs)
    df1.dropna(how='all', axis=1, inplace=True)
if uploaded_file_invoices is not None:
    df2 = my_functions.get_data_from_excel(uploaded_file_invoices)
    df2.dropna(how='all', axis=1, inplace=True)

    df = df[(df["Project No."] == "15195-002") | (df["Project No."] == "15195-008")]
    df[['Discipline', 'Phase' ]] = df['Task'].str.split('-', expand=True)
    df = df.fillna("NA")
    # df['discipline_Name'] =
    totalhoursAD = df.groupby([(df["Transaction Type"] == "Time"), (df["Project No."] == "15195-002")])["Quantity Reg."].sum()
    totalcostAD = df.groupby([(df["Transaction Type"] == "Time"), (df["Project No."] == "15195-002")])["Cost, Reg."].sum()
    totalhoursPAK = df.groupby([(df["Transaction Type"] == "Time"), (df["Project No."] == "15195-008")])["Quantity Reg."].sum()
    totalCostPAK = df.groupby([(df["Transaction Type"] == "Time"), (df["Project No."] == "15195-008")])["Cost, Reg."].sum()
    total_to_invoice = df2["Amount, Currency"].sum()
    total_invoiced = df2[df2["Transferred"] == True]["Amount, Currency"].sum()

    showcards = st.checkbox('show Score Cards')
    if showcards:
        # st.dataframe(df)
        st.header("Timesheet Summary")
        exchangeratePKR = st.number_input("Please input the exchange rate from USD to PKR, 1 USD = xxx PKR",value=285.08)
        exchangerateAED = 3.765
        col100, col200, col300 = st.columns(3, gap="large")
        with col100:
            st.header("Project Hours")
            st.metric(label="Total project hours spent", value=totalhoursPAK[3]+totalhoursAD[3])
            st.metric(label="Total hours AD office", value=(totalhoursAD[3]))
            st.metric(label="Total hours PAK office", value=totalhoursPAK[3])

        with col200:
            st.header("Project Cost")
            st.metric(label="Total Project Cost $", value=round((totalcostAD[3]/exchangerateAED)+(totalCostPAK[3]/exchangeratePKR),2))
            st.metric(label="Total Cost AD office $", value=str(round((totalcostAD[3]/exchangerateAED),2)))
            st.metric(label="Total Cost PAK office $", value=str(round((totalCostPAK[3]/exchangeratePKR),2)))
            st.metric(label="Average hourly Cost AD office $", value=round((totalcostAD[3]/exchangerateAED)/totalhoursAD[3],2))
            st.metric(label="Average hourly Cost PAK office $", value=round((totalCostPAK[3]/exchangeratePKR)/totalhoursPAK[3],2))

        with col300:
            st.header("Invoices")
            st.metric(label="Total to invoice $", value=total_to_invoice)
            st.metric(label="Total Invoiced $", value=round(total_invoiced, 2))
            st.metric(label="Expenses", value=(totalhoursAD[3]))

        my_functions.style_metric_cards(border_left_color="black", background_color="lightgrey", border_size_px=0,
                                        border_color="lightgrey")

    showtimedetails = st.checkbox('show Time&Cost details')
    if showtimedetails:
        lst_projectno = my_functions.unique(df, "Project No.")
        lst_phase = my_functions.unique(df, 'Phase')
        lst_discipline = my_functions.unique(df, 'Discipline')
        lst_transaction = my_functions.unique(df, "Transaction Type")

        project = st.sidebar.selectbox("Project Office", lst_projectno)
        phase = st.sidebar.selectbox("Phase", lst_phase)
        discipline = st.sidebar.selectbox("Discipline", lst_discipline)
        transaction = st.sidebar.selectbox("Transaction Type", lst_transaction)
        # EBS4 = st.sidebar.selectbox(EBS_LEVEL4, lst_EBS4)
        # EBS5 = st.sidebar.selectbox(EBS_LEVEL5, lst_EBS5)
        # FAILURE = st.sidebar.selectbox(FAILURE_MODE, lst_FAILURE, key="fail")
        # PLANT_select = st.sidebar.selectbox(PLANT_NAME, lst_plant)
        # EQUIPMENT = st.sidebar.selectbox(EQUIPMENT_NAME, lst_equip_name)
        # CODE = st.sidebar.selectbox(EVENT_CODE, lst_eventcode)
        #
        mskproject = df["Project No."] != project if project == "All" else df["Project No."] == project
        mskdiscipline = df["Discipline"] != discipline if discipline == "All" else df["Discipline"] == discipline
        mskphase = df["Phase"] != phase if phase == "All" else df["Phase"] == phase
        msktransaction = df["Transaction Type"] != transaction if transaction == "All" else df["Transaction Type"] == transaction
        # msk4 = df[EBS_LEVEL4] != EBS4 if EBS4 == "All" else df[EBS_LEVEL4] == EBS4
        # msk5 = df[EBS_LEVEL5] != EBS5 if EBS5 == "All" else df[EBS_LEVEL5] == EBS5
        # mskfail = df[FAILURE_MODE] != FAILURE if FAILURE == "All" else df[FAILURE_MODE] == FAILURE
        # mskequip = df[EQUIPMENT_NAME] != EQUIPMENT if EQUIPMENT == "All" else df[EQUIPMENT_NAME] == EQUIPMENT
        # mskcode = df[EVENT_CODE] != CODE if CODE == "All" else df[EVENT_CODE] == CODE
        # mskplant = df[PLANT_NAME] != PLANT_select if PLANT_select == "All" else df[PLANT_NAME] == PLANT_select
        #
        df_filtered = (df[mskproject& mskdiscipline&mskphase&msktransaction])[["Project No.","Cost, Reg.", "Phase", "Discipline",
                                                                               "Transaction Type", "Quantity Reg."]]

        total_hours = df_filtered["Quantity Reg."].sum()
        total_cost = df_filtered["Cost, Reg."].sum()

        txt_total_hours = ":red[_**Total**_] hours for this search              :red[**{}** hours]\n". \
            format(round(total_hours))
        txt_total_cost = ":red[_**Total**_] cost for this search        :red[**{}** Adidas]\n". \
            format(round(total_cost))

        st.info(":red[**Use the dropdown selectors at the left pane to select your search criteria**]")
        col30, col40 = st.columns(2, gap="small")
        with col30:
            st.info(txt_total_hours)
        with col40:
            st.write()
            st.info(txt_total_cost)

        st.dataframe(
            df_filtered.groupby(["Project No.", "Phase", "Discipline", "Transaction Type"]).agg(
                Hours=("Quantity Reg.", "sum"),
                Cost=("Cost, Reg.", "sum")).round(), width=3 * 800)

        st.dataframe(df_filtered, width = 3 *800)

        # Document analysis
    showdocanalysis = st.checkbox("Show Document Data")
    if showdocanalysis:

        doc_name = "LOD:DocNo-DocTitle"
        total_docs_count = df1[doc_name].nunique()
        total_disc = df1["LOD:DC*"].nunique()

        total_docs_submitted = df1[(df1["W-Status"] == "Completed/ Submitted") & (df1["Rev"] == "C1")][doc_name].nunique()
        total_docs_approved = df1[(df1["Doc-Status"] == "IFU")&(df1["W-Status"] == "Completed/ Submitted")][doc_name].nunique()
        doc_3_rev_filter = df1[doc_name].value_counts().rename('rev_counts')
        df1 = df1.merge(doc_3_rev_filter.to_frame(),
                                        left_on=doc_name,
                                        right_index=True)
        doc_3_rev = df1[df1.rev_counts > 3][[doc_name, "rev_counts"]].drop_duplicates()
        doc_3_rev_total = df1[df1.rev_counts > 3][doc_name].nunique()
        doc_per_disc = df1.drop_duplicates(subset=doc_name, keep="first")
        doc_per_disc = doc_per_disc["LOD:DC*"].value_counts()
        total_docs_rejected = df1[(df1["Review Code"] == "E")][doc_name].nunique()


        st.write("Total Documents count", total_docs_count)
        st.write("Total No of discipline", total_disc)
        st.write("Total documents submitted", total_docs_submitted, "--> ",
                 (round((total_docs_submitted/total_docs_count)*100,1)), "%")
        st.write("Total Approved documents", total_docs_approved)
        st.write("Total Documents with more than 3 revisions",doc_3_rev_total)
        st.write("rejected",total_docs_rejected)
        col1, col2 = st.columns(2, gap="small")
        with col1:
            st.subheader("Documents per discipline")
            st.write(doc_per_disc)
        with col2:
            st.subheader("Document Revision count")
            st.write(doc_3_rev)
        # st.write(df1)

#Invoices data


