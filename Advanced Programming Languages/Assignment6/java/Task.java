/**
 * Represents a ride request task for the data processing system.
 */
public class Task
{
    private final String identifier;
    private final String payload;  // e.g. "Downtown -> Airport"

    public Task(String identifier, String payload)
    {
        this.identifier = identifier;
        this.payload = payload;
    }

    public String GetIdentifier()
    {
        return identifier;
    }

    public String GetPayload()
    {
        return payload;
    }

    /** Shutdown sentinel: worker that receives this should exit. */
    public static final String ShutdownIdentifier = "__SHUTDOWN__";

    public static boolean IsShutdown(Task task)
    {
        return task != null && ShutdownIdentifier.equals(task.identifier);
    }

    public static Task Shutdown()
    {
        return new Task(ShutdownIdentifier, null);
    }
}
