import streamlit as st

import re

import json



# ---- Streamlit Config ----

st.set_page_config(page_title="ICS Egress Job Parser", layout="wide")



# ---- Login ----

if "authenticated" not in st.session_state:

    st.session_state.authenticated = False



if not st.session_state.authenticated:

    st.title("ICS Egress Job Parser")

    pwd = st.text_input("Enter password:", type="password")

    if st.button("Submit"):

        if pwd == "icscp2025":

            st.session_state.authenticated = True

        else:

            st.error("Incorrect password.")

    st.stop()



# ---- Helper Functions ----

def extract_sql_statements(text):

    sql_pattern = re.compile(

        r"""(?is)(SELECT|INSERT|UPDATE|DELETE|MERGE|CREATE|DROP|WITH)\s.+?\s(FROM|INTO|SET|VALUES|TABLE).+?(;|$)""",

        re.MULTILINE | re.IGNORECASE

    )

    return [match.group(0).strip() for match in sql_pattern.finditer(text)]



def extract_control_logic(text):

    lines = text.splitlines()

    control_json = {

        "commands": [],

        "conditions": [],

        "logging": [],

        "env_vars": [],

        "file_operations": [],

        "schedule": "Not detected"

    }



    for line in lines:

        l = line.strip()

        if re.search(r'(curl\s|-X\s|gsutil|bteq\s|python\s|sh\s|copy\s|scp\s)', l, re.IGNORECASE):

            control_json["commands"].append(l)

        elif re.search(r'exit\s|quit\s|\$?\? -ne 0|IF ERRORCODE', l, re.IGNORECASE):

            control_json["conditions"].append(l)

        elif re.search(r'echo|print\(', l):

            control_json["logging"].append(l)

        elif re.search(r'export\s|client\s*=|os\.environ|set\s', l):

            control_json["env_vars"].append(l)

        elif re.search(r'\/(mnt|ftp|sftp|tmp|exports|archive).*?\.(csv|json|txt|xml)', l):

            control_json["file_operations"].append(l)

        elif re.search(r'cron|interval|@daily|@hourly|\b\d+\s+\d+\s+\*\s+\*\s+\*', l, re.IGNORECASE):

            control_json["schedule"] = l.strip()



    return control_json



# ---- UI Logic ----

st.title("ICS Egress Job Parser")



uploaded_file = st.file_uploader("Upload Egress Job", type=["bteq", "sql", "sh", "py", "java", "cs", "txt", "dtsx"])



if uploaded_file:

    file_contents = uploaded_file.read().decode("utf-8")

    sql_statements = extract_sql_statements(file_contents)

    control_logic_json = extract_control_logic(file_contents)



    parsed_sql = "\n\n".join(sql_statements) if sql_statements else "No SQL statements found."

    control_logic_json_str = json.dumps(control_logic_json, indent=2)



    # Layout: 3 Columns

    col1, col2, col3 = st.columns(3)



    with col1:

        st.subheader("Code Preview")

        st.text_area("Code", file_contents, height=400)



    with col2:

        st.subheader("Parsed SQL")

        st.text_area("SQL Statements", parsed_sql, height=400)

        st.download_button("Download SQL", data=parsed_sql, file_name="parsed_sql.sql")



    with col3:

        st.subheader("Control Logic (Simplified JSON)")

        st.text_area("Control Logic", control_logic_json_str, height=400)

        st.download_button("Download Control JSON", data=control_logic_json_str, file_name="control_logic.json")