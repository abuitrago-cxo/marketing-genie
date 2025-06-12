import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message, StreamEvents } from "@langchain/langgraph-sdk";
import { useState, useEffect, useRef, useCallback } from "react";
import { useConfig } from "./contexts/ConfigContext"; // Import useConfig
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import { ConfigModal } from "./components/ConfigModal"; // Import ConfigModal
import { Button } from "@/components/ui/button"; // Import Button
import { CogIcon } from "lucide-react"; // Import an icon

export default function App() {
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false); // State for modal
  const { llmConfig, isLoading: isConfigLoading } = useConfig(); // Get config status

  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<
    ProcessedEvent[]
  >([]);
  const [historicalActivities, setHistoricalActivities] = useState<
    Record<string, ProcessedEvent[]>
  >({});
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const hasFinalizeEventOccurredRef = useRef(false);

  const thread = useStream<{
    messages: Message[];
    initial_search_query_count: number;
    max_research_loops: number;
    reasoning_model: string;
  }>({
    apiUrl: import.meta.env.DEV
      ? "http://localhost:2024" // Ensure this matches your local LangGraph server from `langgraph dev`
      : window.location.origin, // Uses current window origin for deployed version
    assistantId: "agent", // Matches the key in `LANGSERVE_GRAPHS` in docker-compose.yml
    messagesKey: "messages",
    onFinish: (event: StreamEvents) => {
      // Handle stream finishing, e.g., final AI message or error
      console.log("Stream finished:", event);
    },
    onUpdateEvent: (event: StreamEvents) => {
      // This callback can be used to update UI based on intermediate stream events
      // console.log("Stream update event:", event);
      let processedEvent: ProcessedEvent | null = null;
      if (event.event === "on_chat_model_stream" && event.data?.chunk?.content) {
        // This is a more generic way to handle streaming content if needed
        // For now, we rely on the specific named events below
      }

      // Check for specific named events from the graph
      const graphEvent = event.data?.chunk; // Assuming custom events are in data.chunk
      if (graphEvent?.generate_query) {
        processedEvent = {
          title: "Generating Search Queries",
          data: graphEvent.generate_query.query_list.join(", "),
        };
      } else if (graphEvent?.web_research) {
        const sources = graphEvent.web_research.sources_gathered || [];
        const numSources = sources.length;
        const uniqueLabels = [
          ...new Set(sources.map((s: any) => s.label).filter(Boolean)),
        ];
        const exampleLabels = uniqueLabels.slice(0, 3).join(", ");
        processedEvent = {
          title: "Web Research",
          data: `Gathered ${numSources} sources. Related to: ${
            exampleLabels || "N/A"
          }.`,
        };
      } else if (graphEvent?.reflection) {
        processedEvent = {
          title: "Reflection",
          data: graphEvent.reflection.is_sufficient
            ? "Search successful, generating final answer."
            : `Need more information, searching for ${graphEvent.reflection.follow_up_queries.join(
                ", "
              )}`,
        };
      } else if (graphEvent?.finalize_answer) {
        processedEvent = {
          title: "Generating Search Queries",
          data: event.generate_query.query_list.join(", "),
        };
      } else if (event.web_research) {
        const sources = event.web_research.sources_gathered || [];
        const numSources = sources.length;
        const uniqueLabels = [
          ...new Set(sources.map((s: any) => s.label).filter(Boolean)),
        ];
        const exampleLabels = uniqueLabels.slice(0, 3).join(", ");
        processedEvent = {
          title: "Web Research",
          data: `Gathered ${numSources} sources. Related to: ${
            exampleLabels || "N/A"
          }.`,
        };
      } else if (event.reflection) {
        processedEvent = {
          title: "Reflection",
          data: event.reflection.is_sufficient
            ? "Search successful, generating final answer."
            : `Need more information, searching for ${event.reflection.follow_up_queries.join(
                ", "
              )}`,
        };
      } else if (event.finalize_answer) {
        processedEvent = {
          title: "Finalizing Answer",
          data: "Composing and presenting the final answer.",
        };
        hasFinalizeEventOccurredRef.current = true;
      }
      if (processedEvent) {
        setProcessedEventsTimeline((prevEvents) => [
          ...prevEvents,
          processedEvent!,
        ]);
      }
    },
  });

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [thread.messages]);

  useEffect(() => {
    if (
      hasFinalizeEventOccurredRef.current &&
      !thread.isLoading &&
      thread.messages.length > 0
    ) {
      const lastMessage = thread.messages[thread.messages.length - 1];
      if (lastMessage && lastMessage.type === "ai" && lastMessage.id) {
        setHistoricalActivities((prev) => ({
          ...prev,
          [lastMessage.id!]: [...processedEventsTimeline],
        }));
      }
      hasFinalizeEventOccurredRef.current = false;
    }
  }, [thread.messages, thread.isLoading, processedEventsTimeline]);

  const handleSubmit = useCallback(
    (submittedInputValue: string, effort: string, model: string) => { // 'model' here is for 'reasoning_model'
      const { llmConfig, isLoading: isConfigLoading, } = useConfig(); // Get config and loading state

      if (isConfigLoading || !llmConfig.isLoaded) {
        console.warn("Configuration not loaded yet. Submission prevented.");
        // Optionally, show a user notification here
        return;
      }
      if (!submittedInputValue.trim()) return;

      setProcessedEventsTimeline([]);
      hasFinalizeEventOccurredRef.current = false;

      // Backend configuration from ConfigContext
      // Ensure keys are snake_case as expected by the Python Pydantic model
      const currentConfigForBackend = {
        llm_provider: llmConfig.llmProvider,
        gemini_api_key: llmConfig.geminiApiKey,
        ollama_base_url: llmConfig.ollamaBaseUrl,
        ollama_model_name: llmConfig.ollamaModelName,
        lmstudio_base_url: llmConfig.lmstudioBaseUrl,
        lmstudio_model_name: llmConfig.lmstudioModelName,
        // query_generator_model, reflection_model, answer_model can also be set here
        // if you want the frontend to override the backend defaults for these specific Gemini models.
        // For now, we let the backend handle those defaults unless overridden by these provider settings.
      };

      // Convert effort to initial_search_query_count and max_research_loops
      // low means max 1 loop and 1 query
      // medium means max 3 loops and 3 queries
      // high means max 10 loops and 5 queries
      let initial_search_query_count = 0;
      let max_research_loops = 0;
      switch (effort) {
        case "low":
          initial_search_query_count = 1;
          max_research_loops = 1;
          break;
        case "medium":
          initial_search_query_count = 3;
          max_research_loops = 3;
          break;
        case "high":
          initial_search_query_count = 5;
          max_research_loops = 10;
          break;
      }

      const newMessages: Message[] = [
        ...(thread.messages || []),
        {
          type: "human",
          content: submittedInputValue,
          id: Date.now().toString(),
        },
      ];

      // The first argument to submit is the graph's input schema.
      // The second argument (options) can contain 'configurable'.
      thread.submit(
        {
          messages: newMessages,
          initial_search_query_count: initial_search_query_count,
          max_research_loops: max_research_loops,
          reasoning_model: model, // This 'model' is for the specific 'reasoning_model' input field of the graph
        },
        {
          configurable: currentConfigForBackend,
        }
      );
    },
    [thread, useConfig] // Added useConfig to dependency array
  );

  const handleCancel = useCallback(() => {
    thread.stop();
    window.location.reload();
  }, [thread]);

  return (
    <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
      <main className="flex-1 flex flex-col overflow-hidden max-w-4xl mx-auto w-full">
        {/* Header Area for Settings Button */}
        <div className="p-2 flex justify-end border-b border-neutral-700">
          <Button variant="outline" size="icon" onClick={() => setIsConfigModalOpen(true)} title="Settings">
            <CogIcon className="h-5 w-5" />
          </Button>
        </div>

        {/* Configuration Loading Status/Error Message */}
        {!isConfigLoading && !llmConfig.isLoaded && (
          <div className="p-4 bg-red-800 text-white text-center">
            Failed to load initial LLM configuration. Please check settings or network. Some features may not work correctly.
          </div>
        )}

        {/* Reminder for Web Search Limitation - shown if Ollama or LMStudio is selected */}
        {llmConfig.llmProvider && llmConfig.llmProvider !== "gemini" && (
          <div className="p-2 bg-yellow-700 text-white text-xs text-center">
            Note: Web research capability is only functional when 'Gemini' is selected as the LLM provider.
          </div>
        )}

        <div
          className={`flex-1 overflow-y-auto ${
            thread.messages.length === 0 ? "flex" : ""
          }`}
        >
          {thread.messages.length === 0 ? (
            <WelcomeScreen
              handleSubmit={handleSubmit}
              isLoading={thread.isLoading}
              onCancel={handleCancel}
            />
          ) : (
            <ChatMessagesView
              messages={thread.messages}
              isLoading={thread.isLoading}
              scrollAreaRef={scrollAreaRef}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              liveActivityEvents={processedEventsTimeline}
              historicalActivities={historicalActivities}
            />
          )}
        </div>
      </main>
      <ConfigModal isOpen={isConfigModalOpen} onClose={() => setIsConfigModalOpen(false)} />
    </div>
  );
}
