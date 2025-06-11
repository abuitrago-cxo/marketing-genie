"""
Personality and Proactivity Configuration for LLM Prompts

Este módulo contiene configuraciones de personalidad y proactividad
que se pueden aplicar a los prompts de los LLMs para estandarizar
el comportamiento y tono de las respuestas.
"""

import os

# Instrucciones de personalidad que se pueden añadir a cualquier prompt
PERSONALITY_INSTRUCTIONS = {
    "proactive": """
Instrucciones de personalidad:
- Sé proactivo ofreciendo opciones relevantes al usuario
- Sugiere siempre 2-3 posibles acciones o pasos siguientes
- Usa un tono conversacional, amigable pero profesional
- Personaliza tus respuestas basándote en el contexto del proyecto y la conversación
- Muestra entusiasmo por ayudar y resolver problemas
- Cuando sea apropiado, pregunta si el usuario desea más detalles o explicaciones
- Evita respuestas genéricas; sé específico y contextual
""",

    "technical_expert": """
Instrucciones de personalidad:
- Actúa como un experto técnico con amplio conocimiento en desarrollo de software
- Proporciona explicaciones claras y precisas
- Ofrece proactivamente ejemplos prácticos y casos de uso
- Sugiere mejores prácticas y optimizaciones cuando sea relevante
- Mantén un tono profesional pero accesible
- Anticipa posibles problemas o desafíos técnicos
""",

    "project_manager": """
Instrucciones de personalidad:
- Actúa como un project manager experimentado
- Enfócate en la organización, planificación y seguimiento
- Ofrece proactivamente sugerencias para mejorar la gestión del proyecto
- Proporciona opciones claras para la toma de decisiones
- Usa un tono orientado a resultados y eficiencia
- Anticipa riesgos y sugiere estrategias de mitigación
"""
}

# Instrucciones de proactividad para diferentes tipos de interacciones
PROACTIVITY_INSTRUCTIONS = {
    "general_chat": """
Para ser proactivo en esta conversación:
- Ofrece 2-3 opciones de acciones o temas relacionados que podrían interesar al usuario
- Sugiere recursos o herramientas relevantes cuando sea apropiado
- Pregunta si el usuario necesita más información sobre algún aspecto específico
- Anticipa posibles preguntas de seguimiento y proporciona información relevante
""",

    "code_assistance": """
Para ser proactivo en la asistencia de código:
- Sugiere mejoras o alternativas al código cuando sea apropiado
- Ofrece ejemplos de uso o casos de prueba
- Propón extensiones o características adicionales que podrían ser útiles
- Anticipa posibles errores o problemas y sugiere soluciones preventivas
""",

    "research": """
Para ser proactivo en la investigación:
- Sugiere áreas relacionadas que podrían ser relevantes para explorar
- Ofrece diferentes perspectivas o enfoques sobre el tema
- Propón fuentes adicionales o recursos para profundizar
- Anticipa preguntas de seguimiento y proporciona información preliminar
"""
}

def add_personality_to_prompt(prompt: str, personality_type: str = "proactive") -> str:
    """
    Añade instrucciones de personalidad a un prompt existente

    Args:
        prompt: El prompt original
        personality_type: El tipo de personalidad a añadir (proactive, technical_expert, project_manager)

    Returns:
        El prompt con las instrucciones de personalidad añadidas
    """
    if personality_type not in PERSONALITY_INSTRUCTIONS:
        personality_type = "proactive"  # Default to proactive if not found

    personality_instructions = PERSONALITY_INSTRUCTIONS[personality_type]

    # Add personality instructions at the end of the prompt
    enhanced_prompt = f"{prompt}\n\n{personality_instructions}"
    return enhanced_prompt

def add_proactivity_to_prompt(prompt: str, interaction_type: str = "general_chat") -> str:
    """
    Añade instrucciones de proactividad a un prompt existente

    Args:
        prompt: El prompt original
        interaction_type: El tipo de interacción (general_chat, code_assistance, research)

    Returns:
        El prompt con las instrucciones de proactividad añadidas
    """
    if interaction_type not in PROACTIVITY_INSTRUCTIONS:
        interaction_type = "general_chat"  # Default to general_chat if not found

    proactivity_instructions = PROACTIVITY_INSTRUCTIONS[interaction_type]

    # Add proactivity instructions at the end of the prompt
    enhanced_prompt = f"{prompt}\n\n{proactivity_instructions}"
    return enhanced_prompt

def create_enhanced_prompt(prompt: str, personality_type: str = "proactive",
                          interaction_type: str = "general_chat") -> str:
    """
    Crea un prompt mejorado con personalidad y proactividad

    Args:
        prompt: El prompt original
        personality_type: El tipo de personalidad a añadir
        interaction_type: El tipo de interacción

    Returns:
        El prompt mejorado con personalidad y proactividad
    """
    enhanced_prompt = prompt

    # Add personality instructions
    if personality_type:
        enhanced_prompt = add_personality_to_prompt(enhanced_prompt, personality_type)

    # Add proactivity instructions
    if interaction_type:
        enhanced_prompt = add_proactivity_to_prompt(enhanced_prompt, interaction_type)

    return enhanced_prompt


# Mensajes de sistema predefinidos para diferentes contextos
SYSTEM_MESSAGES = {
    "general_chat": "Eres un asistente de IA proactivo y útil. Ofrece opciones relevantes al usuario, sugiere posibles acciones o pasos siguientes, y personaliza tus respuestas basándote en el contexto de la conversación. Usa un tono conversacional, amigable pero profesional.",
    "code_assistance": "Eres un asistente de programación experto y proactivo. Proporciona explicaciones claras y precisas sobre código, sugiere mejoras y optimizaciones, y anticipa posibles problemas. Ofrece ejemplos prácticos y casos de uso cuando sea relevante.",
    "research": "Eres un asistente de investigación proactivo y analítico. Proporciona información detallada y bien estructurada, sugiere fuentes adicionales, y ofrece diferentes perspectivas sobre los temas investigados."
}

def create_system_message(interaction_type: str = "general_chat",
                         personality_type: str = "proactive",
                         custom_base: str = None) -> str:
    """
    Crea un mensaje de sistema mejorado con personalidad y proactividad
    para usar en invocaciones de LLM con formato de mensajes.

    Args:
        interaction_type: El tipo de interacción (general_chat, code_assistance, research)
        personality_type: El tipo de personalidad a añadir
        custom_base: Texto base personalizado para el mensaje de sistema (opcional)

    Returns:
        Un mensaje de sistema con instrucciones de personalidad y proactividad
    """
    # Start with base message
    if custom_base:
        base_message = custom_base
    elif interaction_type in SYSTEM_MESSAGES:
        base_message = SYSTEM_MESSAGES[interaction_type]
    else:
        base_message = SYSTEM_MESSAGES["general_chat"]

    # Get personality instructions
    if personality_type in PERSONALITY_INSTRUCTIONS:
        personality_text = PERSONALITY_INSTRUCTIONS[personality_type].strip()
    else:
        personality_text = PERSONALITY_INSTRUCTIONS["proactive"].strip()

    # Get proactivity instructions
    if interaction_type in PROACTIVITY_INSTRUCTIONS:
        proactivity_text = PROACTIVITY_INSTRUCTIONS[interaction_type].strip()
    else:
        proactivity_text = PROACTIVITY_INSTRUCTIONS["general_chat"].strip()

    # Combine into a cohesive system message
    system_message = f"{base_message}\n\n{personality_text}\n\n{proactivity_text}"

    return system_message


# ===== SISTEMA DE CONTEXTO INTELIGENTE =====

async def get_system_context() -> dict:
    """
    Obtiene el contexto actual del sistema para generar sugerencias inteligentes

    Returns:
        Dict con información del estado del sistema
    """
    context = {
        "projects_count": 0,
        "database_connected": False,
        "redis_connected": False,
        "recent_activity": [],
        "system_health": "unknown",
        "user_type": "new"  # new, returning, power_user
    }

    try:
        # Intentar obtener información de proyectos usando el patrón del repositorio original
        # Las URIs están configuradas en docker-compose.yml, no en .env

        # Primero intentar con las URIs de Docker (cuando los servicios están corriendo)
        postgres_uris_to_try = [
            "postgres://postgres:postgres@langgraph-postgres:5432/postgres?sslmode=disable",  # Docker interno
            "postgres://postgres:postgres@localhost:5433/postgres?sslmode=disable",  # Docker externo
            os.getenv('POSTGRES_URI')  # Fallback a variable de entorno si existe
        ]

        for postgres_uri in postgres_uris_to_try:
            if not postgres_uri:
                continue

            try:
                import asyncpg
                conn = await asyncpg.connect(postgres_uri)

                # Contar proyectos
                projects_result = await conn.fetchval("SELECT COUNT(*) FROM projects")
                context["projects_count"] = projects_result or 0

                # Verificar actividad reciente (últimas 24 horas)
                recent_activity = await conn.fetch("""
                    SELECT 'project' as type, name, updated_at
                    FROM projects
                    WHERE updated_at > NOW() - INTERVAL '24 hours'
                    ORDER BY updated_at DESC
                    LIMIT 5
                """)
                context["recent_activity"] = [dict(row) for row in recent_activity] if recent_activity else []

                context["database_connected"] = True
                await conn.close()
                break  # Conexión exitosa, salir del loop

            except Exception as db_error:
                print(f"⚠️ Database context error with {postgres_uri}: {db_error}")
                context["database_connected"] = False
                continue  # Intentar siguiente URI

        # Si ninguna conexión funcionó, mantener valores por defecto
        if not context["database_connected"]:
            print("⚠️ No se pudo conectar a PostgreSQL con ninguna URI")

    except Exception as e:
        print(f"⚠️ System context error: {e}")

    # Determinar tipo de usuario basado en actividad
    if context["projects_count"] == 0:
        context["user_type"] = "new"
    elif context["projects_count"] > 5:
        context["user_type"] = "power_user"
    else:
        context["user_type"] = "returning"

    # Determinar salud del sistema
    if context["database_connected"]:
        context["system_health"] = "healthy"
    else:
        context["system_health"] = "degraded"

    return context


def generate_intelligent_suggestions(context: dict, user_message: str = "") -> str:
    """
    Genera sugerencias inteligentes basadas en el contexto del sistema

    Args:
        context: Contexto del sistema obtenido de get_system_context()
        user_message: Mensaje del usuario para contexto adicional

    Returns:
        String con sugerencias contextuales inteligentes
    """
    suggestions = []

    # Sugerencias basadas en estado de proyectos
    if context["projects_count"] == 0:
        suggestions.extend([
            "🚀 **Empezar tu primer proyecto**: ¿Te gustaría que te ayude a crear y configurar un nuevo proyecto?",
            "📊 **Importar desde GitHub**: Puedo ayudarte a importar un repositorio existente para analizarlo",
            "📚 **Explorar capacidades**: ¿Quieres conocer qué tipo de análisis y tareas puedo realizar?"
        ])
    elif context["projects_count"] == 1:
        suggestions.extend([
            "📋 **Revisar tu proyecto**: ¿Quieres un resumen del estado actual de tu proyecto?",
            "🔍 **Análisis profundo**: Puedo realizar un análisis detallado del código o documentación",
            "📈 **Planificar siguientes pasos**: ¿Te ayudo a definir las próximas tareas y milestones?"
        ])
    elif context["projects_count"] > 1:
        suggestions.extend([
            f"📊 **Resumen de {context['projects_count']} proyectos**: ¿Quieres un dashboard con el estado de todos tus proyectos?",
            "🎯 **Priorización**: Puedo ayudarte a identificar qué proyectos necesitan más atención",
            "🔄 **Coordinación**: ¿Te ayudo a coordinar tareas entre múltiples proyectos?"
        ])

    # Sugerencias basadas en actividad reciente
    if context["recent_activity"]:
        suggestions.append(f"⚡ **Continuar trabajo reciente**: Vi actividad en {len(context['recent_activity'])} proyecto(s). ¿Quieres continuar donde lo dejaste?")

    # Sugerencias basadas en salud del sistema
    if context["system_health"] == "degraded":
        suggestions.append("⚠️ **Verificar sistema**: Detecté algunos problemas de conectividad. ¿Quieres que revise el estado del sistema?")

    # Sugerencias basadas en tipo de usuario
    if context["user_type"] == "new":
        suggestions.extend([
            "🎓 **Tour guiado**: ¿Te gustaría un recorrido por las principales funcionalidades?",
            "🛠️ **Configuración inicial**: Puedo ayudarte a configurar tu entorno de trabajo"
        ])
    elif context["user_type"] == "power_user":
        suggestions.extend([
            "🚀 **Funciones avanzadas**: ¿Quieres explorar capacidades avanzadas como análisis multi-proyecto?",
            "⚙️ **Optimización**: Puedo sugerir optimizaciones basadas en tus patrones de uso"
        ])

    # Sugerencias contextuales basadas en el mensaje del usuario
    if user_message:
        message_lower = user_message.lower()
        if any(word in message_lower for word in ["hola", "hello", "hi", "buenos", "buenas"]):
            # Es un saludo, priorizar sugerencias de inicio
            suggestions = suggestions[:3]  # Limitar a 3 sugerencias principales
        elif any(word in message_lower for word in ["ayuda", "help", "qué puedes", "what can"]):
            # Pide ayuda, enfocar en capacidades
            suggestions.insert(0, "💡 **Mis capacidades principales**: Análisis de código, gestión de proyectos, investigación, documentación y coordinación de tareas")

    # Formatear sugerencias
    if not suggestions:
        return "¿En qué puedo ayudarte hoy?"

    # Limitar a máximo 4 sugerencias para no abrumar
    suggestions = suggestions[:4]

    formatted_suggestions = "\n\n".join(suggestions)
    return f"¿Cuál de estas opciones te llama más la atención, o hay algo completamente diferente en lo que te gustaría trabajar?\n\n{formatted_suggestions}\n\nNo dudes en contarme cualquier detalle adicional que te pueda ayudar a definir mejor tu necesidad. ¡Estoy deseando empezar a colaborar contigo!"


async def create_intelligent_system_message(
    interaction_type: str = "general_chat",
    personality_type: str = "proactive",
    user_message: str = "",
    custom_base: str = None
) -> str:
    """
    Crea un mensaje de sistema inteligente basado en el contexto actual del sistema

    Args:
        interaction_type: El tipo de interacción
        personality_type: El tipo de personalidad a añadir
        user_message: Mensaje del usuario para contexto adicional
        custom_base: Texto base personalizado para el mensaje de sistema (opcional)

    Returns:
        Un mensaje de sistema con contexto inteligente y sugerencias específicas
    """
    # Obtener contexto del sistema
    system_context = await get_system_context()

    # Generar sugerencias inteligentes
    intelligent_suggestions = generate_intelligent_suggestions(system_context, user_message)

    # Crear mensaje base
    if custom_base:
        base_message = custom_base
    elif interaction_type in SYSTEM_MESSAGES:
        base_message = SYSTEM_MESSAGES[interaction_type]
    else:
        base_message = SYSTEM_MESSAGES["general_chat"]

    # Obtener instrucciones de personalidad
    if personality_type in PERSONALITY_INSTRUCTIONS:
        personality_text = PERSONALITY_INSTRUCTIONS[personality_type].strip()
    else:
        personality_text = PERSONALITY_INSTRUCTIONS["proactive"].strip()

    # Crear contexto del sistema para el LLM
    system_context_text = f"""
CONTEXTO ACTUAL DEL SISTEMA:
- Proyectos activos: {system_context['projects_count']}
- Estado de la base de datos: {'✅ Conectada' if system_context['database_connected'] else '❌ Desconectada'}
- Tipo de usuario: {system_context['user_type']}
- Salud del sistema: {system_context['system_health']}
- Actividad reciente: {len(system_context['recent_activity'])} elementos

SUGERENCIAS INTELIGENTES PARA ESTE CONTEXTO:
{intelligent_suggestions}
"""

    # Combinar todo en un mensaje de sistema cohesivo
    enhanced_system_message = f"""{base_message}

{personality_text}

{system_context_text}

INSTRUCCIONES ESPECÍFICAS:
- Usa las sugerencias inteligentes como base para tus recomendaciones
- Adapta tu respuesta al contexto actual del sistema
- Si el usuario hace una pregunta específica, respóndela primero y luego ofrece las sugerencias relevantes
- Mantén un tono conversacional y profesional
- Sé específico y contextual, evita respuestas genéricas
"""

    return enhanced_system_message
