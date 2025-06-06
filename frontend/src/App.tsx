import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";
import { useState, useEffect, useRef, useCallback } from "react";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import { LiveActivityPanel } from "@/components/LiveActivityPanel"; // Import LiveActivityPanel

export default function App() {
  const [currentMessages, setCurrentMessages] = useState<Message[]>([]); // New state for messages
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
      ? "http://localhost:2024"
      : "http://localhost:8123",
    assistantId: "agent",
    messagesKey: "messages",
    onFinish: (event: any) => {
      console.log(event);
    },
    onUpdateEvent: (event: any) => {
      let processedEvent: ProcessedEvent | null = null;
      if (event.generate_query) {
        processedEvent = {
          title: "Generating Search Queries",
          data: event.generate_query.query_list,
          dataType: 'query_list',
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
  }, [currentMessages]); // Changed from thread.messages

  useEffect(() => {
    if (
      hasFinalizeEventOccurredRef.current &&
      !thread.isLoading &&
      currentMessages.length > 0 // Changed from thread.messages
    ) {
      const lastMessage = currentMessages[currentMessages.length - 1]; // Changed from thread.messages
      if (lastMessage && lastMessage.type === "ai" && lastMessage.id) {
        setHistoricalActivities((prev) => ({
          ...prev,
          [lastMessage.id!]: [...processedEventsTimeline],
        }));
      }
      hasFinalizeEventOccurredRef.current = false;
    }
  }, [currentMessages, thread.isLoading, processedEventsTimeline]); // Changed from thread.messages

  const handleSubmit = useCallback(
    (submittedInputValue: string, effort: string, model: string) => {
      if (!submittedInputValue.trim()) return;
      setProcessedEventsTimeline([]);
      hasFinalizeEventOccurredRef.current = false;

      // convert effort to, initial_search_query_count and max_research_loops
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
          max_research_loops = 5;
          break;
        case "very-high":
          initial_search_query_count = 5;
          max_research_loops = 10;
          break;
      }

      const newMessages: Message[] = [
        ...currentMessages,
        {
          type: "human",
          content: submittedInputValue,
          id: Date.now().toString(),
        },
      ];
      thread.submit({
        messages: newMessages, // Pass newMessages which includes current + new human message
        initial_search_query_count: initial_search_query_count,
        max_research_loops: max_research_loops,
        reasoning_model: model,
      });
      setCurrentMessages(newMessages); // Update currentMessages state
    },
    [thread, currentMessages, setCurrentMessages] // Added currentMessages and setCurrentMessages
  );

  const handleCancel = useCallback(() => {
    thread.stop();
    window.location.reload();
  }, [thread]);

  const handleNewChat = useCallback(() => {
    if (thread.isLoading) {
      thread.stop();
    }
    setCurrentMessages([]);
    setProcessedEventsTimeline([]);
    setHistoricalActivities({});
    hasFinalizeEventOccurredRef.current = false;
    // NOTE: useStream's thread object doesn't have an explicit init or reset for messages sent via submit.
    // Clearing currentMessages and other local state is the primary way to reset the UI.
    // The next thread.submit will start with the new `currentMessages`.
  }, [thread, setCurrentMessages, setProcessedEventsTimeline, setHistoricalActivities]);


  return (
    <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
      <main className="flex-1 flex flex-col overflow-hidden max-w-4xl mx-auto w-full">
        <div
          className={`flex-1 overflow-y-auto ${
            currentMessages.length === 0 ? "flex" : "" // Changed condition
          }`}
        >
          {currentMessages.length === 0 ? ( // Changed condition
            <WelcomeScreen
              handleSubmit={handleSubmit}
              isLoading={thread.isLoading}
              onCancel={handleCancel}
              // onNewChat={handleNewChat} // Optional: if WelcomeScreen needs a "New Chat" button
            />
          ) : (
            <div className="flex flex-row flex-1 overflow-hidden">
              <div className="w-2/3 overflow-y-auto"> {/* ChatMessagesView container */}
                <ChatMessagesView
                  messages={currentMessages} // Changed from thread.messages
                  isLoading={thread.isLoading}
                  scrollAreaRef={scrollAreaRef}
                  onSubmit={handleSubmit}
                  onCancel={handleCancel} // This is for cancelling active stream
                  onNewChat={handleNewChat} // This is for starting a new chat
                  liveActivityEvents={processedEventsTimeline}
                  historicalActivities={historicalActivities}
                />
              </div>
              <LiveActivityPanel
                liveActivityEvents={processedEventsTimeline}
                isProcessing={thread.isLoading}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
