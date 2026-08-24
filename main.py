import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()

# Inicializar cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------
# Funciones simuladas de Backend / Base de Datos
# ---------------------------------------------------------
def consultar_base_datos_cliente(id_cliente: str):
    print(f"\n[SISTEMA] 🔍 Consultando base de datos de clientes para ID: {id_cliente}...")
    # Simulación de respuesta de DB
    return json.dumps({
        "id_cliente": id_cliente,
        "nombre": "Álvaro Rodríguez",
        "nivel": "Premium",
        "email": "alvaro@example.com"
    })

def consultar_estado_pedido(id_pedido: str):
    print(f"\n[SISTEMA] 📦 Consultando estado del pedido #{id_pedido}...")
    return json.dumps({
        "id_pedido": id_pedido,
        "estado": "En tránsito",
        "fecha_estimada": "Mañana antes de las 6:00 PM",
        "paquetera": "FedEx",
        "guia": "FDX-9823471"
    })

def obtener_catalogo_ofertas():
    print(f"\n[SISTEMA] 🏷️ Consultando catálogo de productos y recomendaciones...")
    return json.dumps([
        {"producto": "Auriculares Noise Cancelling", "precio": "$120 USD", "descuento": "15%"},
        {"producto": "Teclado Mecánico Wireless", "precio": "$85 USD", "descuento": "10%"},
        {"producto": "Monitor 4K 27 pulg", "precio": "$310 USD", "descuento": "5%"}
    ])

# Declaración de Tools para OpenAI Function Calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "consultar_base_datos_cliente",
            "description": "Obtiene la información del perfil del cliente desde la base de datos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_cliente": {"type": "string", "description": "ID único del cliente (ej. CLI-101)"}
                },
                "required": ["id_cliente"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_estado_pedido",
            "description": "Consulta el estado de rastreo de un pedido especificando su ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_pedido": {"type": "string", "description": "Número o ID del pedido (ej. PED-5542)"}
                },
                "required": ["id_pedido"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_catalogo_ofertas",
            "description": "Retorna el catálogo actual de productos destacados y ofertas para recomendar.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

# Mapa de ejecuciones locales
available_functions = {
    "consultar_base_datos_cliente": consultar_base_datos_cliente,
    "consultar_estado_pedido": consultar_estado_pedido,
    "obtener_catalogo_ofertas": obtener_catalogo_ofertas,
}

def ejecutar_chat():
    system_prompt = (
        "Eres un asistente virtual empático, eficiente y profesional de atención al cliente para la tienda TechStore. "
        "Tu objetivo es resolver dudas de envíos, consultar información de clientes y ofrecer recomendaciones. "
        "Cuando necesites datos específicos del cliente o de un paquete, utiliza las herramientas disponibles. "
        "Si el usuario no te da un ID de cliente o pedido, puedes pedirle un dato simulado como 'CLI-101' o 'PED-5001'."
    )

    messages = [{"role": "system", "content": system_prompt}]

    print("==========================================================")
    print("🤖 bienvenido al Sistema de Atención al Cliente (TechStore)")
    print("Escribe 'salir' para finalizar la sesión.")
    print("==========================================================\n")

    while True:
        user_input = input("\n👤 Cliente: ")
        if user_input.lower().strip() in ["salir", "exit", "quit"]:
            print("\n🤖 Asistente: ¡Gracias por contactar a TechStore! Que tengas un excelente día.")
            break

        messages.append({"role": "user", "content": user_input})

        # Primera llamada al modelo
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        # Comprobar si el modelo requiere ejecutar una función/tool
        if response_message.tool_calls:
            messages.append(response_message)
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                # Ejecutar la función simulada de backend
                function_response = function_to_call(**function_args)

                # Responder a OpenAI con el resultado de la función
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })

            # Segunda llamada al modelo para que redacte la respuesta final
            second_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            bot_reply = second_response.choices[0].message.content
            messages.append({"role": "assistant", "content": bot_reply})
            print(f"\n🤖 Asistente: {bot_reply}")
        else:
            bot_reply = response_message.content
            messages.append({"role": "assistant", "content": bot_reply})
            print(f"\n🤖 Asistente: {bot_reply}")

if __name__ == "__main__":
    ejecutar_chat()