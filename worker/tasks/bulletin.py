from worker.celery_app import app
from app.core.database import SessionLocal
from app.models.sensor_reading import SensorReading
from app.models.alert import Alert
from datetime import datetime
from openai import OpenAI
from app.core.config import settings
from weasyprint import HTML
import base64

# pythonREPL
from langchain_experimental.tools import PythonREPLTool
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


@app.task
def generate_bulletin(date_start: str, date_end: str):
    db = SessionLocal()
    try:
        start = datetime.fromisoformat(date_start)
        end = datetime.fromisoformat(date_end)

        readings = (
            db.query(SensorReading)
            .filter(SensorReading.timestamp >= start)
            .filter(SensorReading.timestamp <= end)
            .order_by(SensorReading.timestamp.asc())
            .all()
        )

        alerts = (
            db.query(Alert)
            .filter(Alert.timestamp >= start)
            .filter(Alert.timestamp <= end)
            .order_by(Alert.timestamp.asc())
            .all()
        )

        readings_text = "Readings summary:\n"
        for r in readings:
            readings_text += f"- {r.city} | {r.timestamp} | AQI: {r.aqi} | PM2.5: {r.pm25} | Temp: {r.temperature}°C | Humidity: {r.humidity}%\n"

        alerts_text = "Alerts:\n"
        for a in alerts:
            alerts_text += f"- {a.alert_type.value.upper()} | {a.city} | {a.message}\n"


        # ////////////////// pythonREPL //////////////////
        llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, api_key=settings.OPENAI_API_KEY)
        tools = [PythonREPLTool()]

        template = """
        You are an environmental data analyst for Japan. 
        You have access to a Python REPL to compute statistics on air quality and weather data.
        
        Analyze the following readings and alerts data:
        {input}
        
        Calculate: city averages, highest polluted city, humidity and PM2.5 correlations, and any notable trends.
        Produce a structured statistical summary before drawing conclusions.
        
        Tools: {tools}
        Tool names: {tool_names}
        
        {agent_scratchpad}
        """

        prompt = PromptTemplate.from_template(template)

        agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
        agent_executor = AgentExecutor(agent=agent,
                                       tools=tools,
                                       verbose=True,
                                       handle_parsing_errors=True,
                                       max_iterations=3)

        agent_result = agent_executor.invoke({
            "input": f"{readings_text}\n\n{alerts_text}"
        })

        statistical_summary = agent_result["output"]

        # LLM bulletin generation
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[ # type: ignore
                {"role": "system",
                 "content": "You are an air quality expert analyzing environmental data across Japan. "
                            "Analyze the readings and alerts provided, identify patterns, "
                            "and formulate hypotheses about observed anomalies."},
                {"role": "user",
                 "content": f"{readings_text}\n\n{alerts_text}\n\nStatistical analysis:\n{statistical_summary}"}
            ]
        )
        bulletin_text = response.choices[0].message.content

        html_content = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            h1 {{ border-bottom: 2px solid #333; padding-bottom: 8px; }}
            h2 {{ color: #555; font-size: 14px; margin-bottom: 24px; }}
            h3 {{ color: #333; margin-top: 32px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 13px; }}
            th {{ background-color: #333; color: white; padding: 8px; text-align: left; }}
            td {{ padding: 7px 8px; border-bottom: 1px solid #ddd; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .aqi-good {{ background-color: #a8d5a2; }}
            .aqi-moderate {{ background-color: #ffe066; }}
            .aqi-unhealthy {{ background-color: #ffb347; }}
            .aqi-very-unhealthy {{ background-color: #ff6b6b; color: white; }}
            .alert-spike {{ color: #cc5500; font-weight: bold; }}
            .alert-trend {{ color: #6a0dad; font-weight: bold; }}
            .bulletin {{ line-height: 1.7; font-size: 14px; }}
        </style>
        </head>
        <body>

        <h1>EcoGuard Japan — Environmental Bulletin</h1>
        <h2>{date_start} to {date_end}</h2>

        <h3>Readings</h3>
        <table>
            <tr>
                <th>City</th><th>Timestamp</th><th>AQI</th>
                <th>PM2.5</th><th>Temp (°C)</th><th>Humidity (%)</th>
            </tr>
            {"".join(f'''
            <tr>
                <td>{r.city}</td>
                <td>{r.timestamp.strftime("%Y-%m-%d %H:%M")}</td>
                <td class="{"aqi-good" if r.aqi and r.aqi <= 50 else "aqi-moderate" if r.aqi and r.aqi <= 100 
        else "aqi-unhealthy" if r.aqi and r.aqi <= 150 else "aqi-very-unhealthy"}">{r.aqi}</td>
                <td>{r.pm25 or "—"}</td>
                <td>{r.temperature or "—"}</td>
                <td>{r.humidity or "—"}</td>
            </tr>''' for r in readings)}
        </table>

        <h3>Alerts</h3>
        <table>
            <tr><th>Type</th><th>City</th><th>Message</th></tr>
            {"".join(f'''
            <tr>
                <td class="alert-{a.alert_type.value}">{a.alert_type.value.upper()}</td>
                <td>{a.city}</td>
                <td>{a.message}</td>
            </tr>''' for a in alerts) if alerts else "<tr><td colspan='3'>No alerts for this period.</td></tr>"}
        </table>

        <h3>Analysis</h3>
        <div class="bulletin">{bulletin_text.replace(chr(10), '<br>')}</div>

        </body>
        </html>
        """

        pdf_bytes = HTML(string=html_content).write_pdf()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        return pdf_base64

    finally:
        db.close()