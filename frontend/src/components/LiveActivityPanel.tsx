import { ActivityTimeline, ProcessedEvent } from "./ActivityTimeline";

interface LiveActivityPanelProps {
  liveActivityEvents: ProcessedEvent[];
  isProcessing: boolean;
}

export const LiveActivityPanel: React.FC<LiveActivityPanelProps> = ({
  liveActivityEvents,
  isProcessing,
}) => {
  // Render ActivityTimeline if processing or if there are events to show,
  // ensuring the "Research" header and its state are managed by ActivityTimeline itself.
  return (
    <div className="w-1/3 overflow-y-auto p-4 border-l border-neutral-700 bg-neutral-800 h-full">
      <ActivityTimeline
        processedEvents={liveActivityEvents}
        isLoading={isProcessing}
      />
    </div>
  );
};
