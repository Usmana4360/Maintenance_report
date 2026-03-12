import streamlit as st
import psycopg2
from datetime import date

st.title("Air Compressor Daily Report")

# Form for technicians
with st.form("compressor_form"):

    report_date = st.date_input("Report Date", value=date.today())
    compressor_code = st.text_input("Compressor Code", "1008")

    operational_status = st.text_input(
        "Operational Status", "15kW Compressor Operational"
    )

    oil_temperature = st.number_input("Oil Temperature (°C)", min_value=0, max_value=200)

    pressure = st.number_input("Pressure (MPa)", min_value=0.0, max_value=2.0, format="%.2f")

    on_load_total_time = st.text_input("On Load Total Time (hours)", "04")

    motor_temperature = st.number_input("Motor Temperature (°C)", min_value=0, max_value=200)

    inverter_condition = st.selectbox("Inverter Condition", ["ok", "not ok"])

    hmi_status = st.text_input("HMI Status", "Autoloadings on")

    compressor_fan = st.selectbox("Compressor Fan", ["ok", "not ok"])

    cleaning = st.selectbox("Cleaning Status", ["ok", "not ok"])

    air_tank_water_drain = st.selectbox("Air Tank Water Drain", ["ok", "not ok"])

    submitted = st.form_submit_button("Submit Report")

# When form is submitted
if submitted:

    try:
        def get_connection():
            conn = psycopg2.connect(
                host=st.secrets["database"]["host"],
                port=st.secrets["database"]["port"],
                dbname=st.secrets["database"]["dbname"],
                user=st.secrets["database"]["user"],
                password=st.secrets["database"]["password"]
            )
            return conn

        conn = get_connection()
        cur = conn.cursor()

        record = {
            "report_date": report_date,
            "compressor_code": compressor_code,
            "operational_status": operational_status,
            "oil_temperature": oil_temperature,
            "pressure": pressure,
            "on_load_total_time": on_load_total_time,
            "motor_temperature": motor_temperature,
            "inverter_condition": inverter_condition,
            "hmi_status": hmi_status,
            "compressor_fan": compressor_fan,
            "cleaning": cleaning,
            "air_tank_water_drain": air_tank_water_drain
        }

        insert_query = """
        INSERT INTO air_compressor_reports
        (report_date, compressor_code, operational_status, oil_temperature, pressure,
        on_load_total_time, motor_temperature, inverter_condition, hmi_status,
        compressor_fan, cleaning, air_tank_water_drain)
        VALUES (%(report_date)s, %(compressor_code)s, %(operational_status)s, %(oil_temperature)s, %(pressure)s,
                %(on_load_total_time)s, %(motor_temperature)s, %(inverter_condition)s, %(hmi_status)s,
                %(compressor_fan)s, %(cleaning)s, %(air_tank_water_drain)s)
        """

        cur.execute(insert_query, record)
        conn.commit()

        st.success("✅ Compressor report submitted successfully!")

    except Exception as e:
        st.error(f"Database error: {e}")

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
