import streamlit as st
import pandas as pd
import my_functions
import time
import streamlit as st
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.express as px
import warnings
from PIL import Image
import datetime as datetime
from streamlit_option_menu import option_menu
from scipy import stats
import xlrd as xlrd

st.set_page_config(page_title="", page_icon="",
                   initial_sidebar_state="expanded", menu_items={"About": "Rev 0 - M.Serag"}, layout="wide")

df = my_functions.get_data_from_excel("expenses.xls")
df.dropna(how='all', axis=1, inplace=True)

df1 = my_functions.get_data_from_excel("doc_status.xlsx")
df1.dropna(how='all', axis=1, inplace=True)

df2 = my_functions.get_data_from_excel("Invoicing.xls")
df2.dropna(how='all', axis=1, inplace=True)


# df = df[(df["Project No."] == "15195-002") | (df["Project No."] == "15195-008")]
df[['Discipline', 'Phase' ]] = df['Task'].str.split('-', expand=True)
df['Discipline'] = df['Discipline'].str.rstrip()
df = df.fillna("NA")

df['Date'] = pd.to_datetime(df['Date']).dt.date
today_in_sheet = df['Date'].max()
totalhoursAD = df.groupby([(df["Transaction Type"] == "Time"), (df["Project No."] == "15195-002")])["Quantity Reg."].sum()
totalcostAD = df.groupby([(df["Transaction Type"] == "Time"), (df["Project No."] == "15195-002")])["Cost, Reg."].sum()
totalhoursPAK = df.groupby([(df["Transaction Type"] == "Time"), (df["Project No."] == "15195-008")])["Quantity Reg."].sum()
totalCostPAK = df.groupby([(df["Transaction Type"] == "Time"), (df["Project No."] == "15195-008")])["Cost, Reg."].sum()
total_to_invoice = df2["Amount, Currency"].sum()
total_invoiced = df2[df2["Transferred"] == True]["Amount, Currency"].sum()

time_cum = df.groupby(['Date', 'Discipline', "Project No."])[['Quantity Reg.']].sum().cumsum().reset_index()
time_cum1 = df.groupby(['Date', 'Discipline', "Project No."])[['Quantity Reg.']].sum().reset_index()
# st.write(time_cum)
# st.write(time_cum1)
# st.write(df)
exchangerateAED = 3.765

lst_projectno = my_functions.unique(df, "Project No.")
lst_phase = my_functions.unique(df, 'Phase')
lst_discipline = my_functions.unique(df, 'Discipline')
lst_transaction = my_functions.unique(df, "Transaction Type")

menumain = option_menu("", ["Time & Cost", 'Document', "Invoices"], default_index=0, orientation="horizontal")

if menumain == "Time & Cost":
    timecheckbox = st.checkbox("Show detailed analysis")
    if not timecheckbox:
        exchangeratePKR = st.number_input("1 USD = xxx PKR", value=285.08)

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

        col400, col500 = st.columns(2, gap="large")
        with col400:
            select_hours_radio = st.radio("**Select View**", ["Monthly", "Daily"], horizontal=True)
            if select_hours_radio == "Monthly":
                fig = px.histogram(df, x='Date', y='Quantity Reg.', color="Project No.", barmode='stack', text_auto="",
                                   title="Monthly hours spend")
                fig.update_traces(xbins_size="M1")
                fig.update_layout(bargap=0.1)
                fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")
                st.plotly_chart(fig)
            else:
                fig = px.bar(df, x=df["Date"], y=df["Quantity Reg."], color="Discipline", barmode="stack",
                             title="Daily hours spend")
                fig.update_layout(legend=dict(orientation="v", yanchor="top", y=1, xanchor="center", x=1),
                                  legend_title_text=None)
                st.plotly_chart(fig)
            pie_radio = st.radio("**Select View**", ["Discipline", "Office"], horizontal=True)
            if pie_radio == "Discipline":
                names_pie = "Discipline"
            else:
                names_pie = "Project No."
            time_pie = px.pie(data_frame=df, values="Quantity Reg.", names=names_pie, hole=0.5,)
                                  # color_discrete_sequence=['#2C3E50', '#CACFD2'])
            time_pie.update_traces(textinfo='percent+value+label', title_text="Time Vouchered",
                                   title_font_size=17, textposition='inside')
            time_pie.update_layout(uniformtext_minsize=17, uniformtext_mode='hide')
            time_pie.update_layout(legend=dict(orientation="v", yanchor="top", y=1, xanchor="center", x=1))

            st.plotly_chart(time_pie)
############
        with col500:
            st.write("  ")
            st.write("  ")
            st.write("  ")
            st.write("  ")
            fig = make_subplots(specs=[[{"secondary_y": True}]],)
            # Add traces
            fig.add_trace(
                go.Scatter(x=time_cum["Date"], y=time_cum['Quantity Reg.'], name="Cumulative project hours", ),
                secondary_y=False, )

            fig.add_trace(
                go.Histogram(x=df["Date"], y=df["Quantity Reg."], name="Daily Hours spent", ), secondary_y=True, )

            fig.update_traces(marker_color='blue', marker_line_color='red',
                              marker_line_width=1, opacity=0.5)
            # Add figure title
            fig.update_layout(title_text=f"Total Project Hours till {today_in_sheet} is {df['Quantity Reg.'].sum()}")

            # Set x-axis title
            fig.update_xaxes(title_text="Date")

            # Set y-axes titles
            fig.update_yaxes(title_text="<b>primary</b> Cumulative hours", secondary_y=False)
            fig.update_yaxes(title_text="<b>secondary</b> Daily Hours", secondary_y=True)

            fig.update_layout(legend=dict(orientation="v", yanchor="top", y=1, xanchor="center", x=0.2),
                              legend_title_text=None)

            st.plotly_chart(fig)

    else:

        project = st.sidebar.selectbox("Project Office", lst_projectno)
        phase = st.sidebar.selectbox("Phase", lst_phase)
        discipline = st.sidebar.selectbox("Discipline", lst_discipline)
        transaction = st.sidebar.selectbox("Transaction Type", lst_transaction)

        mskproject = df["Project No."] != project if project == "All" else df["Project No."] == project
        mskdiscipline = df["Discipline"] != discipline if discipline == "All" else df["Discipline"] == discipline
        mskphase = df["Phase"] != phase if phase == "All" else df["Phase"] == phase
        msktransaction = df["Transaction Type"] != transaction if transaction == "All" else df["Transaction Type"] == transaction

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
df1 = df1.rename(columns={'LOD:DocNo-DocTitle': 'doc_title'})
doc_name = "doc_title"
total_docs_count = df1[doc_name].nunique()
total_disc = df1["LOD:DC*"].nunique()

total_docs_submitted = df1[(df1["W-Status"] == "Completed/ Submitted") & (df1["Rev"] == "C1")][doc_name].nunique()
total_docs_approved = df1[(df1["Doc-Status"] == "IFU")&(df1["W-Status"] == "Completed/ Submitted")][doc_name].nunique()
doc_3_rev_filter = df1[doc_name].value_counts().rename('rev_counts')
df1 = df1.merge(doc_3_rev_filter.to_frame(), left_on=doc_name, right_index=True)
doc_3_rev = df1[df1.rev_counts > 3][[doc_name, "rev_counts"]].drop_duplicates().sort_values(by="rev_counts", ascending=False)
doc_3_rev_total = df1[df1.rev_counts > 3][doc_name].nunique()
doc_per_disc = df1.drop_duplicates(subset=doc_name, keep="first")
doc_per_disc_count = doc_per_disc["LOD:DC*"].value_counts()
total_docs_rejected = df1[(df1["Review Code"] == "E")][doc_name].nunique()

docs_submitted_disc = doc_per_disc[(doc_per_disc["W-Status"] == "Completed/ Submitted")
                                   & (df1["Rev"] == "C1")]["LOD:DC*"].value_counts()
doc_per_disc_count=doc_per_disc_count.reset_index()

df_doc_submittal = doc_per_disc_count.merge(docs_submitted_disc.to_frame(), left_on="LOD:DC*", right_index=True)

if menumain == "Document":

    # st.write(docs_submitted_disc)
    # st.write(doc_per_disc)
    col100, col200, col300 = st.columns(3, gap="large")
    with col100:
        st.metric(label="Total Project Documents", value=total_docs_count)
        st.metric(label="Documents Submitted with > 3 revisions", value=doc_3_rev_total)
    with col200:
        st.metric(label = f"{total_docs_submitted} Documents Submitted",
                  value=str(round((total_docs_submitted/total_docs_count)*100,1))+ " %")
        st.metric(label="Total Rejected Revisions", value=total_docs_rejected)


    with col300:
        st.metric(label="Total Approved Documents", value=total_docs_approved)

    my_functions.style_metric_cards(border_left_color="red", background_color="lightgrey", border_size_px=0.5,
                                    border_color="red")

    col1, col2 = st.columns(2, gap="small")
    with col1:

        st.subheader("Document Revision count")
        st.dataframe(doc_3_rev, width=800)

    with col2:
        st.subheader("Documents per discipline & Submittal")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_doc_submittal["LOD:DC*"],
                             y=df_doc_submittal["count_x"],
                             name="Total Docs", text=df_doc_submittal["count_x"], textangle=0, textposition="outside"))
        fig.update_traces(marker_color='red', marker_line_color='rgb(8,48,107)',
                          marker_line_width=1.5, opacity=0.6)
        fig.add_trace(go.Bar(x=df_doc_submittal["LOD:DC*"],
                             y=df_doc_submittal["count_y"],
                             name="Submitted", text=df_doc_submittal["count_y"], textangle=0, textposition="inside"))

        fig.update_layout(title=dict(text="Document status - submittal", font=dict(size=20),
                                     automargin=True, yref='paper'))
        fig.update_layout(
            title={'y': 1, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}, barmode='overlay')
        fig.update_layout(uniformtext_minsize=15, uniformtext_mode='show')
        fig.update_layout(yaxis=dict(title='Document Count', titlefont_size=16, tickfont_size=14),
                          xaxis=dict(title='Discipline', titlefont_size=16, tickfont_size=14))

        fig.update_yaxes()
        st.plotly_chart(fig, use_container_width=True)



    # st.write(df1)

#Invoices data
labels = {True: 'Transfered', False: 'Pending'}
df2['Transferred'] = df2['Transferred'].map(labels)
lst_pie_names = ["invoiced", "to_invoice"]
lst_pie_values = [total_invoiced, total_to_invoice-total_invoiced]
invoice_cum = df2.groupby(['Planned Date', 'Transferred'])[['Amount, Invoice Currency']].sum().cumsum().reset_index()
invoice_cum1 = df2.groupby(['Planned Date', 'Transferred'])[['Amount, Invoice Currency']].sum().reset_index()
# invoice_cum1['Planned Date'] = pd.to_datetime(invoice_cum1['Planned Date'])
invoice_cum1["Planned Date"] = invoice_cum1["Planned Date"].dt.date
if menumain == "Invoices":
    col1, col2 = st.columns(2, gap='small')
    with col1:

        invoices_pie = px.pie(data_frame=df2, values="Amount, Currency", names="Transferred", hole=0.5,
                              color_discrete_sequence = ['#2C3E50','#CACFD2'])
        invoices_pie.update_layout(legend=dict(orientation="v", yanchor="top", y=1, xanchor="center", x=0))
        invoices_pie.update_traces(textinfo='percent+value', title_text="Invoices Submitted", title_font_size= 17)
        st.plotly_chart(invoices_pie)
        st.write(invoice_cum1)

    with col2:

        fig = px.line(invoice_cum, x="Planned Date", y='Amount, Invoice Currency', color="Transferred",
                      color_discrete_sequence = ['#00c100','#CACFD2'])
        fig.update_traces(mode='markers+lines+text')
        fig.update_layout(yaxis=dict(title='Invoiced ($)', titlefont_size=16, tickfont_size=14),
                          xaxis=dict(title='Planned Date', titlefont_size=16, tickfont_size=14))
        fig.add_bar(alignmentgroup="Planned Date",x=invoice_cum1["Planned Date"],
                    y=invoice_cum1["Amount, Invoice Currency"], name="Invoices",opacity=0.75)
        fig.update_layout(legend_title_text=None, legend=dict(orientation="v", yanchor="top", y=0.9, xanchor="center", x=0.9))
        st.plotly_chart(fig)



