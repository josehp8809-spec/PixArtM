import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, time as dtime, timedelta
from database import db
from gemini_client import gemini
from report_exporter import export_excel, export_pdf


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

# SLA thresholds in minutes
SLA_GREEN  = 5
SLA_YELLOW = 30


def _calc_response_times(df):
    """
    Calcula todos los tiempos de respuesta individuales del DataFrame.
    Retorna lista de minutos (float) por cada par INBOUND → OUTBOUND.
    """
    if df.empty:
        return []
    times = []
    for wa_id, group in df.groupby("wa_id"):
        sorted_msgs = group.sort_values("created_at")
        last_inbound = None
        for _, row in sorted_msgs.iterrows():
            if row["type"] == "INBOUND":
                last_inbound = row["created_at"]
            elif last_inbound is not None:
                delta = (row["created_at"] - last_inbound).total_seconds() / 60
                if 0 < delta < 1440:  # ignorar > 24h (sesión abandonada)
                    times.append(delta)
                last_inbound = None
    return times


def _sla_stats(times):
    """
    Clasifica una lista de tiempos de respuesta en los 3 niveles SLA.
    Retorna dict con avg, green, yellow, red, total.
    """
    if not times:
        return {"avg": None, "green": 0, "yellow": 0, "red": 0, "total": 0}
    green  = sum(1 for t in times if t < SLA_GREEN)
    yellow = sum(1 for t in times if SLA_GREEN <= t < SLA_YELLOW)
    red    = sum(1 for t in times if t >= SLA_YELLOW)
    return {
        "avg":    round(sum(times) / len(times), 1),
        "green":  green,
        "yellow": yellow,
        "red":    red,
        "total":  len(times),
    }


def _semaphore_from_sla(sla):
    """
    Determina el color semáforo del agente según el % de respuestas en rojo/amarillo.
    Criterio principal: tiempo de respuesta (SLA).
    """
    total = sla["total"]
    if total == 0:
        return "⚪", "Sin datos"
    red_pct    = sla["red"]    / total * 100
    yellow_pct = sla["yellow"] / total * 100
    avg        = sla["avg"] or 0
    # Rojo: promedio > 30 min  O  más del 30% de respuestas en rojo
    if avg >= SLA_YELLOW or red_pct >= 30:
        return "🔴", "Alerta"
    # Amarillo: promedio > 5 min  O  más del 30% en amarillo
    if avg >= SLA_GREEN or yellow_pct >= 30:
        return "🟡", "Atención"
    return "🟢", "Excelente"


def _build_agent_summary(df, sentiments):
    """Construye un dict {agent: {sent, chats, sla, pos, neu, neg}}."""
    sentiment_map = {s[0]: s[1] for s in sentiments}
    summary = {}

    for agent, group in df.groupby("agent_username"):
        agent = agent or "Sin asignar"
        sent  = len(group[group["type"] != "INBOUND"])
        chats = group["wa_id"].nunique()
        sla   = _sla_stats(_calc_response_times(group))

        # Sentimientos de las conversaciones de este agente
        agent_contacts = group["wa_id"].unique()
        pos = sum(1 for c in agent_contacts if sentiment_map.get(c) == "positivo")
        neu = sum(1 for c in agent_contacts if sentiment_map.get(c) == "neutral")
        neg = sum(1 for c in agent_contacts if sentiment_map.get(c) == "negativo")
        total_analyzed = pos + neu + neg
        neg_pct = (neg / total_analyzed * 100) if total_analyzed else 0

        summary[agent] = {
            "sent": sent, "chats": chats,
            "sla": sla,                        # dict con avg, green, yellow, red, total
            "positive": pos, "neutral": neu, "negative": neg, "neg_pct": neg_pct,
        }
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# RENDER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def render():
    st.title("📊 Reportes e Inteligencia")

    # ── FILTROS ───────────────────────────────────────────────────────────────
    st.markdown("### 🎛️ Filtros del período")
    f1, f2, f3 = st.columns(3)

    with f1:
        today      = date.today()
        start_date = st.date_input("📅 Fecha inicio", today - timedelta(days=7))
        end_date   = st.date_input("📅 Fecha fin", today)

    with f2:
        start_hour = st.slider("⏰ Hora inicio", 0, 23, 8, format="%d:00")
        end_hour   = st.slider("⏰ Hora fin", 0, 23, 20, format="%d:00")

    with f3:
        all_users = db.get_all_users()
        agent_options = ["Todos"] + [u[1] for u in all_users if u[3] in ("agent", "coordinator")]
        selected_agent = st.selectbox("👤 Agente", agent_options)

    start_dt   = datetime.combine(start_date, dtime(start_hour, 0))
    end_dt     = datetime.combine(end_date, dtime(end_hour, 59, 59))
    agent_filter = None if selected_agent == "Todos" else selected_agent

    st.markdown("---")

    # ── CARGAR DATOS ──────────────────────────────────────────────────────────
    raw = db.get_messages_in_period(start_dt, end_dt, agent_filter)

    if not raw:
        st.info("📭 No hay datos para el período y filtros seleccionados.")
        return

    df = pd.DataFrame(raw, columns=["wa_id", "type", "body", "agent_username", "created_at"])
    df["created_at"] = pd.to_datetime(df["created_at"])

    sentiments    = db.get_sentiments(start_date, end_date)
    agent_summary = _build_agent_summary(df, sentiments)

    # ── MÉTRICAS GLOBALES ─────────────────────────────────────────────────────
    all_times   = _calc_response_times(df)
    sla_global  = _sla_stats(all_times)
    total_chats = df["wa_id"].nunique()
    quota       = db.get_quota_usage()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📨 Total mensajes", len(df))
    m2.metric("💬 Conversaciones", total_chats)
    avg_str = f"{sla_global['avg']} min" if sla_global["avg"] else "N/A"
    m3.metric("⏱️ T. respuesta prom.", avg_str)
    m4.metric("📊 Cuota mensual", f"{quota}/15")

    # SLA global breakdown
    if sla_global["total"] > 0:
        s1, s2, s3 = st.columns(3)
        s1.metric("🟢 < 5 min (excelente)",  f"{sla_global['green']}  respuestas",
                  f"{sla_global['green']/sla_global['total']*100:.0f}%")
        s2.metric("🟡 5–30 min (aceptable)", f"{sla_global['yellow']} respuestas",
                  f"{sla_global['yellow']/sla_global['total']*100:.0f}%")
        s3.metric("🔴 > 30 min (falla)",     f"{sla_global['red']}    respuestas",
                  f"{sla_global['red']/sla_global['total']*100:.0f}%")

    st.markdown("---")

    # ── SEMÁFORO DE AGENTES ───────────────────────────────────────────────────
    st.markdown("### 🚦 Estado por Agente")

    if not agent_summary:
        st.info("Sin datos de agentes en este período.")
    else:
        # Encabezado de columnas
        h1,h2,h3,h4,h5,h6,h7,h8 = st.columns([2,1,1,1.2,1.2,1.2,1.8,1.2])
        for col, txt in zip([h1,h2,h3,h4,h5,h6,h7,h8],
                            ["Agente","Enviados","Chats","🟢 <5min","🟡 5-30m","🔴 >30min","T.Resp.Prom","Estado"]):
            col.markdown(f"**{txt}**")
        st.divider()

        for agent, stats in agent_summary.items():
            sla  = stats["sla"]
            icon, label = _semaphore_from_sla(sla)
            avg_str = f"{sla['avg']} min" if sla["avg"] else "N/A"
            analyzed = stats["positive"] + stats["neutral"] + stats["negative"]
            sent_str = f"😊{stats['positive']} 😐{stats['neutral']} 😠{stats['negative']}" if analyzed else "Sin analizar"

            c1,c2,c3,c4,c5,c6,c7,c8 = st.columns([2,1,1,1.2,1.2,1.2,1.8,1.2])
            with c1: st.markdown(f"**@{agent}**  ")  ; st.caption(sent_str)
            with c2: st.write(stats['sent'])
            with c3: st.write(stats['chats'])
            with c4: st.markdown(f"🟢 **{sla['green']}**")
            with c5: st.markdown(f"🟡 **{sla['yellow']}**")
            with c6: st.markdown(f"🔴 **{sla['red']}**")
            with c7: st.write(avg_str)
            with c8: st.markdown(f"{icon} **{label}**")
            st.divider()

    st.markdown("---")

    # ── ANÁLISIS DE SENTIMIENTOS CON GEMINI ──────────────────────────────────
    st.markdown("### 🤖 Análisis de Sentimientos con Gemini")

    if not gemini.is_configured:
        st.warning("⚠️ Gemini no configurado. Ve a ⚙️ Configuración → Gemini AI.")
    else:
        conversations = df["wa_id"].unique().tolist()
        already = {s[0] for s in sentiments}
        pending = [c for c in conversations if c not in already]

        if pending:
            st.info(f"Hay **{len(pending)}** conversaciones sin analizar en este período.")
        else:
            st.success(f"✅ Las **{len(conversations)}** conversaciones ya fueron analizadas.")

        if conversations:
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                run_all = st.button(
                    f"🔍 Analizar {'todo' if not pending else f'{len(pending)} pendientes'}",
                    type="primary", use_container_width=True
                )
            with col_btn2:
                run_feedback = st.button(
                    "📋 Generar Feedback por Agente",
                    use_container_width=True,
                    disabled=not sentiments
                )

            if run_all:
                _run_sentiment_analysis(
                    pending if pending else conversations,
                    start_dt, end_dt
                )
                st.rerun()

            if run_feedback:
                _run_agent_feedback(agent_summary, df, start_dt, end_dt)

    st.markdown("---")

    # ── GRÁFICAS ──────────────────────────────────────────────────────────────
    st.markdown("### 📈 Visualizaciones")
    tab1, tab2, tab3 = st.tabs(["📊 Volumen por hora", "👤 Por agente", "🧠 Sentimientos"])

    with tab1:
        df_hour = df.copy()
        df_hour["hour"] = df_hour["created_at"].dt.hour
        vol = df_hour.groupby(["hour", "type"]).size().reset_index(name="count")
        if not vol.empty:
            fig = px.bar(vol, x="hour", y="count", color="type", barmode="group",
                         title="Mensajes por hora del día",
                         labels={"hour": "Hora", "count": "Mensajes", "type": "Tipo"},
                         color_discrete_map={"INBOUND": "#0A84FF", "OUTBOUND_REPLY": "#30D158"})
            fig.update_layout(paper_bgcolor="#000", plot_bgcolor="#111", font_color="#FFF")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        by_agent = df.groupby(["agent_username", "type"]).size().reset_index(name="count")
        if not by_agent.empty:
            fig2 = px.bar(by_agent, x="agent_username", y="count", color="type", barmode="group",
                          title="Mensajes por agente",
                          labels={"agent_username": "Agente", "count": "Mensajes"},
                          color_discrete_map={"INBOUND": "#0A84FF", "OUTBOUND_REPLY": "#30D158"})
            fig2.update_layout(paper_bgcolor="#000", plot_bgcolor="#111", font_color="#FFF")
            st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        if sentiments:
            sent_counts = {"positivo": 0, "neutral": 0, "negativo": 0}
            for s in sentiments:
                sent_counts[s[1]] = sent_counts.get(s[1], 0) + 1
            df_sent = pd.DataFrame(list(sent_counts.items()), columns=["Sentimiento", "Cantidad"])
            fig3 = px.pie(df_sent, values="Cantidad", names="Sentimiento",
                          title="Distribución de sentimientos",
                          color_discrete_map={
                              "positivo": "#30D158",
                              "neutral": "#FF9F0A",
                              "negativo": "#FF3B30"
                          })
            fig3.update_layout(paper_bgcolor="#000", font_color="#FFF")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Ejecuta el análisis de sentimientos para ver esta gráfica.")

    st.markdown("---")

    # ── TABLA DE CONVERSACIONES ───────────────────────────────────────────────
    st.markdown("### 📋 Conversaciones del período")
    sentiment_map = {s[0]: (s[1], s[2], s[3]) for s in sentiments}

    table_data = []
    for wa_id, group in df.groupby("wa_id"):
        last_msg = group["created_at"].max()
        agent    = group["agent_username"].dropna().iloc[-1] if not group["agent_username"].dropna().empty else "—"
        msgs     = len(group)
        sent_info = sentiment_map.get(wa_id, (None, False, None))
        sent_icon = {"positivo": "😊", "negativo": "😠", "neutral": "😐"}.get(sent_info[0], "❓")
        alert_icon = "⚠️" if sent_info[1] else ""
        table_data.append({
            "Contacto": f"+{wa_id}",
            "Agente": f"@{agent}",
            "Mensajes": msgs,
            "Sentimiento": f"{sent_icon} {sent_info[0] or 'Sin analizar'}",
            "Urgente": alert_icon or "—",
            "Razón": sent_info[2] or "—",
            "Última actividad": last_msg.strftime("%d/%m/%Y %H:%M") if pd.notna(last_msg) else "—",
        })

    if table_data:
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── EXPORTACIÓN ───────────────────────────────────────────────────────────
    st.markdown("### 📤 Exportar reporte")
    e1, e2 = st.columns(2)

    with e1:
        try:
            excel_bytes = export_excel(df, agent_summary, sentiments, start_dt, end_dt)
            st.download_button(
                "📗 Descargar Excel (.xlsx)",
                data=excel_bytes,
                file_name=f"nyme_{start_date}_{end_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception as ex:
            st.error(f"Error generando Excel: {ex}")

    with e2:
        feedback_store = st.session_state.get("agent_feedbacks", {})
        try:
            pdf_bytes = export_pdf(df, agent_summary, sentiments, start_dt, end_dt, feedback_store)
            st.download_button(
                "📄 Descargar PDF ejecutivo",
                data=pdf_bytes,
                file_name=f"nyme_{start_date}_{end_date}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as ex:
            st.error(f"Error generando PDF: {ex}")


# ─────────────────────────────────────────────────────────────────────────────
# SUB-FUNCIONES DE ANÁLISIS
# ─────────────────────────────────────────────────────────────────────────────

def _run_sentiment_analysis(conversations, start_dt, end_dt):
    total    = len(conversations)
    progress = st.progress(0, text="Iniciando análisis...")
    log_box  = st.container()
    red_list = []

    for i, wa_id in enumerate(conversations):
        progress.progress((i + 1) / total, text=f"Analizando {i+1}/{total}: +{wa_id}")
        msgs = db.get_messages(wa_id)
        msgs_in_period = [
            m for m in msgs
            if m[2] and start_dt <= m[2] <= end_dt  # created_at is index 2
        ]
        if not msgs_in_period:
            continue
        result = gemini.analyze_sentiment(msgs_in_period)
        if result:
            db.save_sentiment(
                wa_id, start_dt.date(),
                result.get("sentiment", "neutral"),
                result.get("urgent", False),
                result.get("reason", ""),
            )
            with log_box:
                sentiment = result.get("sentiment", "neutral")
                urgent    = result.get("urgent", False)
                reason    = result.get("reason", "")
                if urgent or sentiment == "negativo":
                    st.error(f"🔴 +{wa_id} — {reason}")
                    red_list.append(wa_id)
                elif sentiment == "neutral":
                    st.warning(f"🟡 +{wa_id} — {reason}")
                else:
                    st.success(f"🟢 +{wa_id} — {reason}")

    progress.progress(1.0, text="✅ Análisis completado")
    if red_list:
        st.error(f"⚠️ **{len(red_list)} conversación(es) requieren atención inmediata.**")
    else:
        st.success("✅ No se detectaron conversaciones críticas en este período.")


def _run_agent_feedback(agent_summary, df, start_dt, end_dt):
    feedbacks = {}
    agents    = list(agent_summary.keys())
    progress  = st.progress(0, text="Generando feedback con Gemini...")

    for i, agent in enumerate(agents):
        progress.progress((i + 1) / len(agents), text=f"Analizando @{agent}...")
        stats = agent_summary[agent]
        sla   = stats["sla"]

        gemini_stats = {
            "sent":     stats["sent"],
            "chats":    stats["chats"],
            "avg_rt":   sla["avg"],
            "positive": stats["positive"],
            "neutral":  stats["neutral"],
            "negative": stats["negative"],
            # SLA breakdown
            "sla_green":  sla["green"],
            "sla_yellow": sla["yellow"],
            "sla_red":    sla["red"],
            "sla_total":  sla["total"],
        }
        feedback = gemini.generate_agent_feedback(agent, [], gemini_stats)
        if feedback:
            feedbacks[agent] = feedback
            with st.expander(f"📋 Feedback para @{agent}", expanded=True):
                # Mostrar SLA mini-resumen antes del feedback
                col1, col2, col3 = st.columns(3)
                col1.metric("🟢 Excelentes",  sla["green"])
                col2.metric("🟡 Aceptables",  sla["yellow"])
                col3.metric("🔴 Fallas SLA",  sla["red"])
                st.markdown(feedback)

    progress.progress(1.0, text="✅ Feedback generado")
    st.session_state["agent_feedbacks"] = feedbacks
