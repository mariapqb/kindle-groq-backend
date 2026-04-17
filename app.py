import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "groq/compound-mini")


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "ok": True,
        "message": "Backend Groq con web search funcionando"
    })


@app.route("/ask", methods=["POST"])
def ask():
    if not GROQ_API_KEY:
        return jsonify({"error": "Falta configurar GROQ_API_KEY"}), 500

    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()

    if not prompt:
        return jsonify({"error": "La pregunta está vacía"}), 400

    try:
        client = Groq(api_key=GROQ_API_KEY)

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Responde siempre en español, de forma clara, útil y natural. "
                        "Usa búsqueda web cuando la pregunta requiera verificación externa o actualidad. "
                        "Si el usuario pregunta por una persona y el nombre parece tener errores ortográficos, "
                        "intenta identificar primero la coincidencia pública más probable. "
                        "Para hacerlo, no te bases solo en la similitud del nombre: "
                        "usa también el contexto geográfico, político, institucional, académico, profesional o temático presente en la pregunta. "
                        "Da más peso a coincidencias conocidas dentro del país, región o ámbito mencionado por el usuario. "
                        "Por ejemplo, si la pregunta menciona Colombia, universidad, vicepresidencia, política, Quindío o un cargo público, "
                        "prioriza coincidencias relacionadas con ese contexto antes que otras opciones menos relevantes. "
                        "Si encuentras una coincidencia fuerte, responde con frases como "
                        "'Probablemente te refieres a...' y luego resume la información pública encontrada. "
                        "No te limites a decir que no encontraste el nombre exacto si hay una coincidencia razonable apoyada por el contexto. "
                        "Evita proponer listas arbitrarias de apellidos o nombres poco útiles. "
                        "Si no hay una coincidencia plausible incluso con el contexto, entonces sí indica que no encontraste resultados confiables. "
                        "Cuando haya información pública útil, organízala así: "
                        "1) posible coincidencia, "
                        "2) resumen, "
                        "3) fuentes. "
                        "No inventes datos ni afirmes como seguro algo que no esté respaldado."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=900
        )

        response_text = completion.choices[0].message.content

        return jsonify({
            "response": response_text
        })

    except Exception as e:
        return jsonify({
            "error": f"Error consultando Groq: {str(e)}"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)