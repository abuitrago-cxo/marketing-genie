# 🤖 Sistema de Chat Inteligente con Contexto del Sistema

## 📋 Descripción General

El sistema de chat inteligente implementa **acotaciones contextuales dinámicas** basadas en el estado actual del sistema, proporcionando sugerencias específicas y relevantes según:

- **Estado de proyectos** (cantidad, actividad reciente)
- **Conectividad de la base de datos**
- **Tipo de usuario** (nuevo, recurrente, power user)
- **Salud del sistema** (servicios funcionando correctamente)
- **Contexto del mensaje** (saludos, peticiones de ayuda, etc.)

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **`get_system_context()`** - Obtiene el estado actual del sistema
2. **`generate_intelligent_suggestions()`** - Genera sugerencias basadas en contexto
3. **`create_intelligent_system_message()`** - Crea prompts inteligentes para el LLM
4. **`simple_chat_response_node()`** - Nodo LangGraph mejorado con contexto

### Flujo de Funcionamiento

```
Usuario envía mensaje
        ↓
Obtener contexto del sistema
        ↓
Generar sugerencias inteligentes
        ↓
Crear prompt contextual
        ↓
Enviar a LLM (Gemini)
        ↓
Respuesta con acotaciones específicas
```

## 🎯 Tipos de Sugerencias por Contexto

### 👤 Usuario Nuevo (0 proyectos)
- 🚀 **Empezar primer proyecto**
- 📊 **Importar desde GitHub**
- 📚 **Explorar capacidades**
- 🎓 **Tour guiado**
- 🛠️ **Configuración inicial**

### 🔄 Usuario Recurrente (1 proyecto)
- 📋 **Revisar proyecto actual**
- 🔍 **Análisis profundo**
- 📈 **Planificar siguientes pasos**

### 💪 Usuario Power (5+ proyectos)
- 📊 **Dashboard de múltiples proyectos**
- 🎯 **Priorización de proyectos**
- 🔄 **Coordinación entre proyectos**
- 🚀 **Funciones avanzadas**
- ⚙️ **Optimización de flujos**

### ⚠️ Sistema con Problemas
- 🔧 **Verificar conectividad**
- 🛠️ **Diagnóstico del sistema**
- 📞 **Contactar soporte**

### ⚡ Actividad Reciente Detectada
- 🔄 **Continuar trabajo reciente**
- 📋 **Resumen de cambios**
- 🎯 **Próximas acciones sugeridas**

## 🔧 Implementación Técnica

### Obtención del Contexto del Sistema

```python
async def get_system_context() -> dict:
    context = {
        "projects_count": 0,
        "database_connected": False,
        "recent_activity": [],
        "system_health": "unknown",
        "user_type": "new"
    }
    
    # Consultar base de datos PostgreSQL
    # Verificar conectividad Redis
    # Analizar actividad reciente
    # Determinar tipo de usuario
    
    return context
```

### Generación de Sugerencias Inteligentes

```python
def generate_intelligent_suggestions(context: dict, user_message: str = "") -> str:
    suggestions = []
    
    # Lógica basada en cantidad de proyectos
    if context["projects_count"] == 0:
        suggestions.extend([...])  # Sugerencias para usuarios nuevos
    elif context["projects_count"] == 1:
        suggestions.extend([...])  # Sugerencias para un proyecto
    # ... más lógica contextual
    
    return formatted_suggestions
```

### Integración con LangGraph

```python
async def simple_chat_response_node(state: OverallState, config: RunnableConfig):
    # Crear mensaje de sistema inteligente
    intelligent_system_message = await create_intelligent_system_message(
        interaction_type="general_chat",
        personality_type="proactive",
        user_message=user_message
    )
    
    # Enviar a LLM con contexto enriquecido
    prompt_messages = [
        {"role": "system", "content": intelligent_system_message},
        {"role": "user", "content": user_message}
    ]
    
    response = llm.invoke(prompt_messages)
    return {"messages": updated_messages}
```

## 📊 Ejemplos de Respuestas Contextuales

### Escenario 1: Usuario Nuevo
**Input:** "hola"
**Contexto:** 0 proyectos, base de datos conectada
**Output:** 
```
¡Hola! Encantado de ayudarte. Dime, ¿en qué puedo serte útil hoy?

🚀 **Empezar tu primer proyecto**: ¿Te gustaría que te ayude a crear y configurar un nuevo proyecto?

📊 **Importar desde GitHub**: Puedo ayudarte a importar un repositorio existente para analizarlo

📚 **Explorar capacidades**: ¿Quieres conocer qué tipo de análisis y tareas puedo realizar?
```

### Escenario 2: Usuario con Proyectos Activos
**Input:** "¿qué puedes hacer?"
**Contexto:** 3 proyectos, actividad reciente
**Output:**
```
Puedo ayudarte con muchas cosas. Basándome en tu actividad actual:

📊 **Resumen de 3 proyectos**: ¿Quieres un dashboard con el estado de todos tus proyectos?

⚡ **Continuar trabajo reciente**: Vi actividad en 2 proyecto(s). ¿Quieres continuar donde lo dejaste?

🎯 **Priorización**: Puedo ayudarte a identificar qué proyectos necesitan más atención
```

### Escenario 3: Problemas del Sistema
**Input:** "hola"
**Contexto:** Base de datos desconectada
**Output:**
```
Hola! Noto algunos problemas de conectividad en el sistema.

⚠️ **Verificar sistema**: Detecté algunos problemas de conectividad. ¿Quieres que revise el estado del sistema?

🛠️ **Modo limitado**: Puedo ayudarte con funciones básicas mientras se resuelven los problemas de conectividad
```

## 🧪 Testing y Validación

### Script de Pruebas
```bash
cd backend
python test_intelligent_chat.py
```

### Casos de Prueba Cubiertos
- ✅ Obtención de contexto del sistema
- ✅ Generación de sugerencias por tipo de usuario
- ✅ Creación de mensajes de sistema inteligentes
- ✅ Conectividad con base de datos
- ✅ Manejo de errores y fallbacks

## 🚀 Beneficios del Sistema

### Para el Usuario
- **Experiencia Personalizada**: Sugerencias relevantes al contexto actual
- **Onboarding Inteligente**: Guía específica para usuarios nuevos
- **Productividad Mejorada**: Acciones sugeridas basadas en el estado del trabajo
- **Recuperación de Contexto**: Continuación inteligente del trabajo previo

### Para el Sistema
- **Engagement Mejorado**: Usuarios más comprometidos con sugerencias relevantes
- **Reducción de Fricción**: Menos tiempo buscando qué hacer
- **Utilización Óptima**: Mejor uso de las capacidades del sistema
- **Feedback Contextual**: Información del estado del sistema integrada

## 🔄 Próximas Mejoras

### Funcionalidades Planificadas
- [ ] **Memoria de Preferencias**: Recordar preferencias del usuario
- [ ] **Análisis de Patrones**: Sugerencias basadas en comportamiento histórico
- [ ] **Integración con Calendario**: Sugerencias basadas en horarios y deadlines
- [ ] **Notificaciones Proactivas**: Alertas inteligentes sobre proyectos
- [ ] **Métricas de Engagement**: Tracking de efectividad de sugerencias

### Optimizaciones Técnicas
- [ ] **Cache de Contexto**: Optimizar consultas frecuentes
- [ ] **Contexto Distribuido**: Soporte para múltiples instancias
- [ ] **A/B Testing**: Experimentación con diferentes tipos de sugerencias
- [ ] **Machine Learning**: Personalización automática basada en uso

## 📚 Referencias y Documentación

- **Archivo Principal**: `backend/src/agent/utils/prompt_personality.py`
- **Nodo LangGraph**: `backend/src/agent/graph.py` - `simple_chat_response_node`
- **Tests**: `backend/test_intelligent_chat.py`
- **Configuración**: Variables de entorno `GEMINI_API_KEY`, `POSTGRES_URI`
